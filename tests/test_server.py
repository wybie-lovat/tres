import pytest
import json
from unittest.mock import patch, MagicMock, AsyncMock

from tres.models import Wallet, Transaction, BlockRange
from tres.sync import synchronizer


def test_health_check(test_app):
    """Test the health check endpoint"""
    response = test_app.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_start_sync_success(test_app, setup_test_db, monkeypatch):
    """Test successful transaction synchronization via API"""
    # Mock the synchronizer's sync_transactions method
    async def mock_sync_transactions(address, start_block, end_block):
        # Create a wallet and block range in the test database
        wallet, _ = Wallet.get_or_create(address=address)
        BlockRange.create(
            wallet=wallet,
            start_block=start_block,
            end_block=end_block
        )
        return f"Sync completed for wallet {address}"
    
    # Apply the mock
    monkeypatch.setattr(synchronizer, "sync_transactions", mock_sync_transactions)
    
    # Make the API request
    response = test_app.post(
        "/start_sync",
        json={
            "address": "0x1111111111111111111111111111111111111111",
            "start_block": 12345000,
            "end_block": 12345999
        }
    )
    
    # Verify the response
    assert response.status_code == 200
    assert response.json() == {"message": "Sync completed for wallet 0x1111111111111111111111111111111111111111"}
    
    # Verify that the wallet and block range were created
    assert Wallet.select().count() == 1
    assert BlockRange.select().count() == 1


def test_start_sync_error(test_app, setup_test_db, monkeypatch):
    """Test error handling during transaction synchronization via API"""
    # Mock the synchronizer's sync_transactions method to raise an exception
    async def mock_sync_transactions(address, start_block, end_block):
        raise Exception("Test error")
    
    # Apply the mock
    monkeypatch.setattr(synchronizer, "sync_transactions", mock_sync_transactions)
    
    # Make the API request
    response = test_app.post(
        "/start_sync",
        json={
            "address": "0x1111111111111111111111111111111111111111",
            "start_block": 12345000,
            "end_block": 12345999
        }
    )
    
    # Verify the response
    assert response.status_code == 500
    assert "Test error" in response.json()["detail"]
    
    # Verify that no wallet or block range was created
    assert Wallet.select().count() == 0
    assert BlockRange.select().count() == 0


def test_get_transactions_success(test_app, setup_test_db, sample_wallet, sample_block_range, sample_transaction):
    """Test successful retrieval of transactions via API"""
    # Make the API request
    response = test_app.get(f"/transactions?address={sample_wallet.address}")
    
    # Verify the response
    assert response.status_code == 200
    data = response.json()
    
    # Verify the transactions
    assert len(data["transactions"]) == 1
    tx = data["transactions"][0]
    assert tx["hash"] == sample_transaction.hash
    assert tx["block_number"] == sample_transaction.block_number
    assert tx["from_addr"] == sample_transaction.from_addr
    assert tx["to"] == sample_transaction.to
    assert tx["value"] == sample_transaction.value
    
    # Verify the block ranges
    assert len(data["block_ranges"]) == 1
    br = data["block_ranges"][0]
    assert br["start_block"] == sample_block_range.start_block
    assert br["end_block"] == sample_block_range.end_block


def test_get_transactions_wallet_not_found(test_app, setup_test_db):
    """Test error handling when wallet is not found"""
    # Make the API request with a non-existent wallet address
    response = test_app.get("/transactions?address=0x9999999999999999999999999999999999999999")
    
    # Verify the response
    assert response.status_code == 404
    assert "not found" in response.json()["detail"]


def test_get_transactions_empty(test_app, setup_test_db, sample_wallet):
    """Test retrieval of transactions when there are none"""
    # Make the API request
    response = test_app.get(f"/transactions?address={sample_wallet.address}")
    
    # Verify the response
    assert response.status_code == 200
    data = response.json()
    
    # Verify that there are no transactions or block ranges
    assert len(data["transactions"]) == 0
    assert len(data["block_ranges"]) == 0


def test_request_validation(test_app):
    """Test validation of request parameters"""
    # Test with missing fields
    response = test_app.post(
        "/start_sync",
        json={
            "address": "0x1111111111111111111111111111111111111111"
            # Missing start_block and end_block
        }
    )
    assert response.status_code == 422
    
    # Test with invalid address format
    response = test_app.post(
        "/start_sync",
        json={
            "address": "invalid_address",
            "start_block": 12345000,
            "end_block": 12345999
        }
    )
    assert response.status_code == 422
    
    # Test with invalid block range (end < start)
    response = test_app.post(
        "/start_sync",
        json={
            "address": "0x1111111111111111111111111111111111111111",
            "start_block": 12345999,
            "end_block": 12345000  # Less than start_block
        }
    )
    assert response.status_code == 422
