import aiohttp
import logging
import asyncio
from typing import TypedDict, List, Any, Union, Dict, Optional
from aiohttp.client_exceptions import ClientError, ClientResponseError, ClientConnectorError, ServerTimeoutError


class EtherscanTransaction(TypedDict):
    blockNumber: str
    timeStamp: str
    hash: str
    nonce: str
    blockHash: str
    transactionIndex: str
    fromAddr: str
    to: str
    value: str
    gas: str
    gasPrice: str
    isError: str
    txreceipt_status: str
    input: str
    contractAddress: str
    cumulativeGasUsed: str
    gasUsed: str
    confirmations: str
    methodId: str
    functionName: str


class EtherscanResponse(TypedDict):
    status: str
    message: str
    result: Any


class EtherscanTransactionListResponse(EtherscanResponse):
    result: List[EtherscanTransaction]


class EtherscanErrorResponse(EtherscanResponse):
    result: str


# Configure logging
logger = logging.getLogger(__name__)

class EtherscanTransactionsApi:
    def __init__(self, api_key: str):
        self.__api_key = api_key
        self.base_url = 'https://api.etherscan.io/api'
        self.timeout = 30  # seconds

    async def _validate_address(self, address: str) -> bool:
        """Validate Ethereum address format."""
        return address.startswith('0x') and len(address) == 42
    
    async def _handle_response(self, response: aiohttp.ClientResponse) -> Dict[str, Any]:
        """Handle API response and common error cases."""
        if response.status == 200:
            try:
                response_data = await response.json()
                return response_data
            except Exception as e:
                logger.error(f"Failed to parse JSON response: {e}")
                raise ValueError(f"Invalid JSON response from Etherscan API: {e}")
        elif response.status == 429:
            logger.warning("Etherscan API rate limit exceeded")
            raise ValueError("Etherscan API rate limit exceeded. Please try again later.")
        elif response.status >= 500:
            logger.error(f"Etherscan API server error: {response.status}")
            raise ValueError(f"Etherscan API server error: {response.status}")
        else:
            error_text = await response.text()
            logger.error(f"Etherscan API error: {response.status} - {error_text}")
            raise ValueError(f"Etherscan API error: {response.status} - {error_text}")
    
    async def get_transactions(self, address: str, start_block: int, end_block: int, page: int, offset: int) -> Union[EtherscanTransactionListResponse, EtherscanErrorResponse]:
        """Get transactions for an Ethereum address within a block range.
        
        Args:
            address: Ethereum address to get transactions for
            start_block: Starting block number
            end_block: Ending block number
            page: Page number for pagination
            offset: Number of transactions per page
            
        Returns:
            API response with transaction data or error
            
        Raises:
            ValueError: For invalid inputs or API errors
            ClientError: For network-related errors
        """
        # Validate inputs
        if not await self._validate_address(address):
            logger.error(f"Invalid Ethereum address format: {address}")
            raise ValueError(f"Invalid Ethereum address format: {address}")
        
        if start_block < 0 or end_block < start_block:
            logger.error(f"Invalid block range: {start_block}-{end_block}")
            raise ValueError(f"Invalid block range: {start_block}-{end_block}")
        
        params = {
            'module': 'account',
            'action': 'txlist',
            'address': address,
            'startblock': start_block,
            'endblock': end_block,
            'page': page,
            'offset': offset,
            'sort': 'asc',
            'apikey': self.__api_key
        }
        
        logger.info(f"Requesting transactions for {address} (blocks {start_block}-{end_block}, page {page})")
        
        try:
            timeout = aiohttp.ClientTimeout(total=self.timeout)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.get(self.base_url, params=params) as response:
                    response_data = await self._handle_response(response)
                    
                    # Check for API-level errors in successful HTTP responses
                    if response_data.get('status') == '0':
                        error_message = response_data.get('message', 'Unknown error')
                        result = response_data.get('result', '')
                        
                        # Special case: "No transactions found" is not an error
                        if result and "No transactions found" in result:
                            logger.info(f"No transactions found for {address} in blocks {start_block}-{end_block}")
                            return response_data
                        
                        # Check for rate limiting
                        if "rate limit" in error_message.lower() or "rate limit" in str(result).lower():
                            logger.warning("Etherscan API rate limit reached")
                            raise ValueError("Etherscan API rate limit reached. Please try again later.")
                        
                        logger.warning(f"Etherscan API returned error: {error_message} - {result}")
                    
                    # Process successful responses with transaction list
                    if response_data.get('status') == '1' and isinstance(response_data.get('result'), list):
                        tx_count = len(response_data['result'])
                        logger.info(f"Retrieved {tx_count} transactions for {address}")
                        
                        # Convert 'from' to 'fromAddr' in each transaction for consistency
                        for tx in response_data['result']:
                            if 'from' in tx:
                                tx['fromAddr'] = tx.pop('from')
                    
                    return response_data
                    
        except ClientConnectorError as e:
            logger.error(f"Connection error to Etherscan API: {e}")
            raise ValueError(f"Failed to connect to Etherscan API: {e}")
        except ServerTimeoutError as e:
            logger.error(f"Timeout connecting to Etherscan API: {e}")
            raise ValueError(f"Etherscan API request timed out after {self.timeout} seconds")
        except ClientResponseError as e:
            logger.error(f"Error response from Etherscan API: {e}")
            raise ValueError(f"Etherscan API error: {e}")
        except ClientError as e:
            logger.error(f"Client error with Etherscan API: {e}")
            raise ValueError(f"Network error when connecting to Etherscan API: {e}")
        except asyncio.TimeoutError:
            logger.error(f"Request to Etherscan API timed out after {self.timeout} seconds")
            raise ValueError(f"Request timed out after {self.timeout} seconds")
        except Exception as e:
            logger.error(f"Unexpected error with Etherscan API: {e}", exc_info=True)
            raise ValueError(f"Error fetching transactions: {e}")
