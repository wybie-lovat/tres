import os
import time
from typing import List, Any, Optional, Dict
from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks, Request, Response, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel, Field, validator
import uvicorn
import logging
from datetime import datetime
from peewee import DoesNotExist, IntegrityError

from .sync import synchronizer
from .models import Wallet, Transaction, BlockRange
from .database import db, connect_db, close_db

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(title="Ethereum Transaction Sync API")

# Rate limiting configuration
rate_limit_data: Dict[str, Dict[str, Any]] = {}

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Exception handlers
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    logger.error(f"Validation error: {exc}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "detail": "Invalid request parameters",
            "errors": exc.errors()
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "An unexpected error occurred",
            "message": str(exc)
        }
    )

# Set up templates and static files
templates_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "templates")
static_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static")

# Create directories if they don't exist
os.makedirs(templates_dir, exist_ok=True)
os.makedirs(static_dir, exist_ok=True)

templates = Jinja2Templates(directory=templates_dir)
app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Request and response models
class SyncRequest(BaseModel):
    address: str = Field(..., description="Ethereum wallet address", pattern=r"^0x[a-fA-F0-9]{40}$")
    start_block: int = Field(..., description="Start block number", ge=0)
    end_block: int = Field(..., description="End block number", ge=0)
    
    @validator('end_block')
    def end_block_must_be_greater_than_start_block(cls, v, values):
        if 'start_block' in values and v < values['start_block']:
            raise ValueError('end_block must be greater than or equal to start_block')
        return v

class SyncResponse(BaseModel):
    message: str

class TransactionResponse(BaseModel):
    block_number: int
    time_stamp: str
    hash: str
    from_addr: str
    to: Optional[str]
    value: str
    gas: str
    gas_price: str
    is_error: bool
    function_name: Optional[str]

class BlockRangeResponse(BaseModel):
    start_block: int
    end_block: int

class TransactionsResponse(BaseModel):
    transactions: List[TransactionResponse]
    block_ranges: List[BlockRangeResponse]

# Database connection dependency
async def get_db():
    try:
        connect_db()
        yield
    except Exception as e:
        logger.error(f"Database connection error: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database connection failed"
        )
    finally:
        close_db()

# Rate limiting middleware
async def check_rate_limit(request: Request, limit_per_minute: int = 60):
    client_ip = request.client.host
    current_time = time.time()
    
    # Initialize or get client data
    if client_ip not in rate_limit_data:
        rate_limit_data[client_ip] = {
            "requests": [],
            "blocked_until": 0
        }
    
    client_data = rate_limit_data[client_ip]
    
    # Check if client is blocked
    if client_data["blocked_until"] > current_time:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Rate limit exceeded. Try again in {int(client_data['blocked_until'] - current_time)} seconds."
        )
    
    # Remove old requests
    minute_ago = current_time - 60
    client_data["requests"] = [req for req in client_data["requests"] if req > minute_ago]
    
    # Check rate limit
    if len(client_data["requests"]) >= limit_per_minute:
        # Block for 30 seconds
        client_data["blocked_until"] = current_time + 30
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded. Try again in 30 seconds."
        )
    
    # Add current request
    client_data["requests"].append(current_time)

# Routes
@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """Serve the index page with the transaction sync UI."""
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/start_sync", response_model=SyncResponse)
async def start_sync(request: SyncRequest, background_tasks: BackgroundTasks, client_request: Request):
    try:
        # Check rate limit - more strict for sync operations
        await check_rate_limit(client_request, limit_per_minute=10)
        
        # Log the sync request
        logger.info(f"Sync requested for address {request.address} from block {request.start_block} to {request.end_block}")
        
        # Validate address format
        if not request.address.startswith('0x') or len(request.address) != 42:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid Ethereum address format"
            )
        
        # Check if block range is reasonable (prevent excessive ranges)
        if request.end_block - request.start_block > 1000000:  # 1 million blocks is ~6 months
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Block range too large. Please limit to 1,000,000 blocks per request."
            )
        
        try:
            # Call the synchronizer to sync transactions
            message = await synchronizer.sync_transactions(
                address=request.address,
                start_block=request.start_block,
                end_block=request.end_block
            )
            
            return {"message": message}
            
        except IntegrityError as e:
            logger.warning(f"Integrity error during sync: {e}")
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="A sync with this data already exists"
            )
        except Exception as e:
            logger.error(f"Error during sync: {e}", exc_info=True)
            if "rate limit" in str(e).lower():
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="Etherscan API rate limit reached. Please try again later."
                )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
                detail=f"Sync failed: {str(e)}"
            )
    
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Unexpected error in start_sync: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {str(e)}"
        )

@app.get("/transactions", response_model=TransactionsResponse)
async def get_transactions(address: str, client_request: Request, _: Any = Depends(get_db)):
    try:
        # Check rate limit
        await check_rate_limit(client_request, limit_per_minute=30)
        
        # Validate address format
        if not address.startswith('0x') or len(address) != 42:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid Ethereum address format"
            )
        
        # Log the request
        logger.info(f"Transactions requested for address {address}")
        
        # Get the wallet by address
        try:
            wallet = Wallet.get(Wallet.address == address)
        except DoesNotExist:
            logger.info(f"Wallet {address} not found")
            # Return empty data instead of 404 for better UX
            return {
                "transactions": [],
                "block_ranges": [],
                "message": f"No data found for address {address}"
            }
        
        # Get transactions for the wallet
        transactions = Transaction.select().where(Transaction.wallet == wallet).order_by(Transaction.block_number.desc())
        
        # Get block ranges for the wallet
        block_ranges = BlockRange.select().where(BlockRange.wallet == wallet).order_by(BlockRange.start_block)
        
        # Format the response
        return {
            "transactions": [
                {
                    "block_number": tx.block_number,
                    "time_stamp": tx.time_stamp.isoformat(),
                    "hash": tx.hash,
                    "from_addr": tx.from_addr,
                    "to": tx.to,
                    "value": tx.value,
                    "gas": tx.gas,
                    "gas_price": tx.gas_price,
                    "is_error": tx.is_error,
                    "function_name": tx.function_name
                }
                for tx in transactions
            ],
            "block_ranges": [
                {
                    "start_block": br.start_block,
                    "end_block": br.end_block
                }
                for br in block_ranges
            ]
        }
    
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Error retrieving transactions: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve transactions: {str(e)}"
        )

# Health check endpoint
@app.get("/health")
async def health_check(response: Response):
    try:
        # Try to connect to the database
        connect_db()
        db_status = "connected"
        close_db()
    except Exception as e:
        logger.warning(f"Database health check failed: {e}")
        db_status = "disconnected"
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    
    return {
        "status": "ok" if db_status == "connected" else "degraded",
        "timestamp": datetime.now().isoformat(),
        "database": db_status,
        "api_version": "1.0.0"
    }

# Run the server if this file is executed directly
if __name__ == "__main__":
    uvicorn.run("tres.server:app", host="0.0.0.0", port=8000, reload=True)
