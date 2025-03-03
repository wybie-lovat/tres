import os
import pytest
import asyncio
from datetime import datetime
from typing import Dict, List, Any, Optional
from unittest import mock

import peewee
from peewee import SqliteDatabase
from httpx import AsyncClient
from fastapi.testclient import TestClient

# Mock the database connection before importing models
with mock.patch('peewee.PostgresqlDatabase'):
    from tres.models import BaseModel, Wallet, Transaction, BlockRange
from tres.etherscan import EtherscanTransactionsApi, EtherscanTransactionListResponse, EtherscanErrorResponse
from tres.server import app
from tres.sync import TransactionSynchronizer

# Define test database
test_db = SqliteDatabase(':memory:')

# Models to create in test database
MODELS = [Wallet, Transaction, BlockRange]

# Mock Etherscan API response data
MOCK_TRANSACTION = {
    "blockNumber": "12345678",
    "timeStamp": "1609459200",  # 2021-01-01 00:00:00
    "hash": "0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef",
    "nonce": "42",
    "blockHash": "0xabcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890",
    "transactionIndex": "10",
    "fromAddr": "0x1111111111111111111111111111111111111111",
    "to": "0x2222222222222222222222222222222222222222",
    "value": "1000000000000000000",  # 1 ETH
    "gas": "21000",
    "gasPrice": "50000000000",
    "isError": "0",
    "txreceipt_status": "1",
    "input": "0x",
    "contractAddress": "",
    "cumulativeGasUsed": "1000000",
    "gasUsed": "21000",
    "confirmations": "100",
    "methodId": "0x",
    "functionName": ""
}

# Mock successful API response
MOCK_SUCCESS_RESPONSE = {
    "status": "1",
    "message": "OK",
    "result": [MOCK_TRANSACTION]
}

# Mock error API response
MOCK_ERROR_RESPONSE = {
    "status": "0",
    "message": "NOTOK",
    "result": "Error! Invalid address format"
}


class MockEtherscanTransactionsApi(EtherscanTransactionsApi):
    """Mock Etherscan API for testing"""
    
    def __init__(self, api_key: str = "fake_api_key", should_fail: bool = False):
        super().__init__(api_key)
        self.should_fail = should_fail
        self.calls = []
    
    async def get_transactions(
        self, address: str, start_block: int, end_block: int, page: int, offset: int
    ) -> Dict[str, Any]:
        """Mock implementation that returns predefined responses"""
        # Record the API call
        self.calls.append({
            "address": address,
            "start_block": start_block,
            "end_block": end_block,
            "page": page,
            "offset": offset
        })
        
        # Return error or success based on configuration
        if self.should_fail:
            return MOCK_ERROR_RESPONSE
        else:
            # If it's not the first page, return empty result to simulate end of data
            if page > 1:
                return {
                    "status": "1",
                    "message": "OK",
                    "result": []
                }
            return MOCK_SUCCESS_RESPONSE


@pytest.fixture
def test_app(setup_test_db):
    """Create a test FastAPI application with dependencies overridden"""
    # Override database dependency
    from tres.server import get_db
    
    # Create a test dependency override
    async def override_get_db():
        try:
            yield
        finally:
            pass
    
    # Apply the override
    app.dependency_overrides[get_db] = override_get_db
    
    # Create test client
    client = TestClient(app)
    return client


@pytest.fixture
def setup_test_db():
    """Set up an in-memory SQLite database for testing"""
    # Create a patch for the database
    with mock.patch('tres.models.db') as mock_db:
        # Configure the test database
        test_db.bind(MODELS, bind_refs=False, bind_backrefs=False)
        test_db.connect()
        test_db.create_tables(MODELS)
        
        # Replace with test database
        for model in MODELS:
            model._meta.database = test_db
        
        # Provide the test database
        yield test_db
        
        # Clean up
        test_db.drop_tables(MODELS)
        test_db.close()


@pytest.fixture
def mock_etherscan_api():
    """Create a mock Etherscan API instance"""
    return MockEtherscanTransactionsApi()


@pytest.fixture
def mock_failing_etherscan_api():
    """Create a mock Etherscan API instance that returns errors"""
    return MockEtherscanTransactionsApi(should_fail=True)


@pytest.fixture
def mock_synchronizer(mock_etherscan_api):
    """Create a TransactionSynchronizer with mock API"""
    synchronizer = TransactionSynchronizer()
    synchronizer.api = mock_etherscan_api
    return synchronizer


@pytest.fixture
def sample_wallet(setup_test_db):
    """Create a sample wallet in the test database"""
    wallet = Wallet.create(address="0x1111111111111111111111111111111111111111")
    return wallet


@pytest.fixture
def sample_block_range(setup_test_db, sample_wallet):
    """Create a sample block range in the test database"""
    block_range = BlockRange.create(
        wallet=sample_wallet,
        start_block=12345000,
        end_block=12345999
    )
    return block_range


@pytest.fixture
def sample_transaction(setup_test_db, sample_wallet):
    """Create a sample transaction in the test database"""
    transaction = Transaction.create(
        wallet=sample_wallet,
        block_number=12345678,
        time_stamp=datetime.fromtimestamp(1609459200),
        hash="0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef",
        nonce="42",
        block_hash="0xabcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890",
        transaction_index="10",
        from_addr="0x1111111111111111111111111111111111111111",
        to="0x2222222222222222222222222222222222222222",
        value="1000000000000000000",
        gas="21000",
        gas_price="50000000000",
        is_error=False,
        txreceipt_status="1",
        input="0x",
        contract_address=None,
        cumulative_gas_used="1000000",
        gas_used="21000",
        confirmations="100",
        method_id="0x",
        function_name=""
    )
    return transaction
