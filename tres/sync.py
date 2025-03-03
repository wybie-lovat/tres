import os
import asyncio
import datetime
import time
import logging
from typing import List, Dict, Any, Optional, Tuple, Union
from dotenv import load_dotenv
from peewee import IntegrityError, DoesNotExist

from .etherscan import EtherscanTransactionsApi
from .models import Wallet, Transaction, BlockRange
from .database import db, connect_db, close_db

# Load environment variables
load_dotenv()

# Get Etherscan API key from environment variables
ETHERSCAN_API_KEY = os.getenv("ETHERSCAN_API_KEY", "")

# Configure logging
logger = logging.getLogger(__name__)

class TransactionSynchronizer:
    def __init__(self):
        self.api = EtherscanTransactionsApi(ETHERSCAN_API_KEY)
        self.max_retries = 3
        self.retry_delay = 2  # seconds
    
    async def _retry_api_call(self, func, *args, **kwargs) -> Dict[str, Any]:
        """Retry an API call with exponential backoff."""
        last_exception = None
        for attempt in range(self.max_retries):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                last_exception = e
                logger.warning(f"API call failed (attempt {attempt+1}/{self.max_retries}): {str(e)}")
                # Check if it's a rate limit error
                if "rate limit" in str(e).lower():
                    # Exponential backoff with jitter
                    delay = self.retry_delay * (2 ** attempt) + (0.1 * attempt * time.time() % 1)
                    logger.info(f"Rate limit hit, waiting {delay:.2f} seconds before retry")
                    await asyncio.sleep(delay)
                else:
                    # For other errors, use a shorter delay
                    await asyncio.sleep(self.retry_delay)
        
        # If we get here, all retries failed
        logger.error(f"All {self.max_retries} API call attempts failed")
        raise last_exception
    
    async def _check_existing_block_ranges(self, wallet: Wallet, start_block: int, end_block: int) -> Tuple[bool, List[Dict[str, int]]]:
        """Check if there are overlapping block ranges already synced."""
        try:
            # Get existing block ranges for this wallet
            existing_ranges = BlockRange.select().where(BlockRange.wallet == wallet)
            
            # Check for overlaps
            overlaps = []
            for br in existing_ranges:
                # Check if ranges overlap
                if not (br.end_block < start_block or br.start_block > end_block):
                    overlaps.append({
                        "start_block": br.start_block,
                        "end_block": br.end_block
                    })
            
            return bool(overlaps), overlaps
        except Exception as e:
            logger.error(f"Error checking existing block ranges: {e}")
            return False, []
    
    async def _save_transactions(self, wallet: Wallet, transactions: List[Dict[str, Any]]) -> int:
        """Save transactions to the database and return count of new transactions."""
        new_tx_count = 0
        duplicates = 0
        errors = 0
        
        with db.atomic():
            for tx_data in transactions:
                try:
                    # Convert timestamp to datetime
                    try:
                        timestamp = datetime.datetime.fromtimestamp(
                            int(tx_data.get('timeStamp', 0))
                        )
                    except (ValueError, OverflowError):
                        logger.warning(f"Invalid timestamp in transaction {tx_data.get('hash')}, using current time")
                        timestamp = datetime.datetime.now()
                    
                    # Safely get integer values with fallbacks
                    try:
                        block_number = int(tx_data.get('blockNumber', 0))
                    except ValueError:
                        block_number = 0
                    
                    # Create or update the transaction
                    tx, created = Transaction.get_or_create(
                        hash=tx_data.get('hash'),
                        defaults={
                            'wallet': wallet,
                            'block_number': block_number,
                            'time_stamp': timestamp,
                            'nonce': tx_data.get('nonce', ''),
                            'block_hash': tx_data.get('blockHash', ''),
                            'transaction_index': tx_data.get('transactionIndex', ''),
                            'from_addr': tx_data.get('from', ''),  # Note: API returns 'from' not 'fromAddr'
                            'to': tx_data.get('to', None),
                            'value': tx_data.get('value', '0'),
                            'gas': tx_data.get('gas', '0'),
                            'gas_price': tx_data.get('gasPrice', '0'),
                            'is_error': tx_data.get('isError', '0') == '1',
                            'txreceipt_status': tx_data.get('txreceipt_status', None),
                            'input': tx_data.get('input', ''),
                            'contract_address': tx_data.get('contractAddress', None),
                            'cumulative_gas_used': tx_data.get('cumulativeGasUsed', '0'),
                            'gas_used': tx_data.get('gasUsed', '0'),
                            'confirmations': tx_data.get('confirmations', '0'),
                            'method_id': tx_data.get('methodId', None),
                            'function_name': tx_data.get('functionName', None)
                        }
                    )
                    
                    if created:
                        new_tx_count += 1
                    else:
                        duplicates += 1
                        
                except IntegrityError as e:
                    logger.warning(f"Integrity error saving transaction {tx_data.get('hash')}: {e}")
                    duplicates += 1
                except Exception as e:
                    logger.error(f"Error saving transaction {tx_data.get('hash')}: {e}")
                    errors += 1
        
        logger.info(f"Processed {len(transactions)} transactions: {new_tx_count} new, {duplicates} duplicates, {errors} errors")
        return new_tx_count
    
    async def sync_transactions(self, address: str, start_block: int, end_block: int) -> str:
        """Synchronize transactions for a wallet address within the specified block range."""
        # Connect to the database
        connect_db()
        block_range = None
        total_transactions = 0
        
        try:
            # Validate inputs
            if not address.startswith('0x') or len(address) != 42:
                raise ValueError("Invalid Ethereum address format")
            
            if start_block < 0 or end_block < start_block:
                raise ValueError("Invalid block range")
            
            # Create or get the wallet
            try:
                wallet, created = Wallet.get_or_create(address=address)
                if created:
                    logger.info(f"Created new wallet record for {address}")
            except IntegrityError as e:
                logger.error(f"Database integrity error creating wallet: {e}")
                raise ValueError(f"Could not create wallet record: {str(e)}")
            
            # Check for overlapping block ranges
            has_overlaps, overlaps = await self._check_existing_block_ranges(wallet, start_block, end_block)
            if has_overlaps:
                overlap_str = ", ".join([f"{o['start_block']}-{o['end_block']}" for o in overlaps])
                logger.warning(f"Overlapping block ranges found for {address}: {overlap_str}")
                # We'll continue anyway but log the warning
            
            # Create the block range record
            try:
                block_range = BlockRange.create(
                    wallet=wallet,
                    start_block=start_block,
                    end_block=end_block
                )
                logger.info(f"Created block range record {start_block}-{end_block} for {address}")
            except IntegrityError as e:
                logger.error(f"Block range already exists: {e}")
                raise ValueError("This exact block range has already been synced for this address")
            
            # Fetch transactions from Etherscan
            page = 1
            offset = 1000  # Number of transactions per page
            total_pages_processed = 0
            max_pages = 100  # Safety limit to prevent infinite loops
            
            while page <= max_pages:
                try:
                    logger.info(f"Fetching page {page} of transactions for {address} (blocks {start_block}-{end_block})")
                    
                    # Use retry mechanism for API calls
                    response = await self._retry_api_call(
                        self.api.get_transactions,
                        address=address,
                        start_block=start_block,
                        end_block=end_block,
                        page=page,
                        offset=offset
                    )
                    
                    # Check if the response is successful
                    if response.get('status') != '1':
                        error_message = response.get('message', 'Unknown error')
                        result = response.get('result', '')
                        
                        # Special handling for "No transactions found" which is not an error
                        if "No transactions found" in result:
                            logger.info(f"No transactions found for {address} in blocks {start_block}-{end_block}")
                            break
                        
                        # Handle rate limiting
                        if "rate limit" in error_message.lower() or "rate limit" in str(result).lower():
                            logger.warning("Etherscan API rate limit reached, waiting before retry")
                            await asyncio.sleep(5)  # Wait 5 seconds before retry
                            continue
                        
                        raise Exception(f"Etherscan API error: {error_message} - {result}")
                    
                    # Get the transactions from the response
                    transactions = response.get('result', [])
                    
                    # If no transactions are returned, we're done
                    if not transactions:
                        logger.info(f"No more transactions found for {address} on page {page}")
                        break
                    
                    # Process and save transactions
                    new_tx_count = await self._save_transactions(wallet, transactions)
                    total_transactions += new_tx_count
                    
                    # If we got fewer transactions than the offset, we're done
                    if len(transactions) < offset:
                        logger.info(f"Reached end of transactions (got {len(transactions)} < {offset})")
                        break
                    
                    # Otherwise, move to the next page
                    page += 1
                    total_pages_processed += 1
                    
                    # Add a small delay to avoid hitting rate limits
                    await asyncio.sleep(0.2)
                    
                except Exception as e:
                    logger.error(f"Error processing page {page}: {e}")
                    # If we've already processed some pages successfully, don't fail the whole sync
                    if total_pages_processed > 0:
                        logger.warning(f"Sync partially completed with {total_pages_processed} pages processed")
                        break
                    else:
                        raise
            
            if page > max_pages:
                logger.warning(f"Reached maximum page limit ({max_pages}) for {address}")
            
            # Update the block range with transaction count
            if block_range:
                block_range.transaction_count = total_transactions
                block_range.save()
            
            result_message = f"Sync completed for wallet {address}: {total_transactions} new transactions found"
            if total_transactions == 0:
                result_message += " (no new transactions)"
            
            logger.info(result_message)
            return result_message
        
        except ValueError as e:
            # Handle validation errors
            logger.error(f"Validation error: {e}")
            # If there's an error, delete the block range record if it was created
            if block_range:
                block_range.delete_instance()
            raise ValueError(str(e))
        
        except Exception as e:
            # Handle other errors
            logger.error(f"Sync error: {e}", exc_info=True)
            # If there's an error, delete the block range record if it was created
            if block_range:
                block_range.delete_instance()
            raise Exception(f"Transaction sync failed: {str(e)}")
        
        finally:
            # Always close the database connection
            close_db()

# Create a singleton instance
synchronizer = TransactionSynchronizer()
