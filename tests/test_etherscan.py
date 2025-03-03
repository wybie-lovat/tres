import pytest
import asyncio
from unittest.mock import patch, MagicMock

from tres.etherscan import EtherscanTransactionsApi, EtherscanTransaction


@pytest.mark.asyncio
async def test_get_transactions_success(mock_etherscan_api):
    """Test successful transaction retrieval from Etherscan API"""
    # Call the API
    response = await mock_etherscan_api.get_transactions(
        address="0x1111111111111111111111111111111111111111",
        start_block=12345000,
        end_block=12345999,
        page=1,
        offset=10
    )
    
    # Verify the response
    assert response["status"] == "1"
    assert response["message"] == "OK"
    assert len(response["result"]) == 1
    
    # Verify the transaction data
    tx = response["result"][0]
    assert tx["hash"] == "0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef"
    assert tx["fromAddr"] == "0x1111111111111111111111111111111111111111"
    assert tx["to"] == "0x2222222222222222222222222222222222222222"
    assert tx["blockNumber"] == "12345678"
    
    # Verify that the API was called with the correct parameters
    assert len(mock_etherscan_api.calls) == 1
    call = mock_etherscan_api.calls[0]
    assert call["address"] == "0x1111111111111111111111111111111111111111"
    assert call["start_block"] == 12345000
    assert call["end_block"] == 12345999
    assert call["page"] == 1
    assert call["offset"] == 10


@pytest.mark.asyncio
async def test_get_transactions_error(mock_failing_etherscan_api):
    """Test error handling in Etherscan API"""
    # Call the API
    response = await mock_failing_etherscan_api.get_transactions(
        address="invalid_address",
        start_block=12345000,
        end_block=12345999,
        page=1,
        offset=10
    )
    
    # Verify the response
    assert response["status"] == "0"
    assert response["message"] == "NOTOK"
    assert response["result"] == "Error! Invalid address format"
    
    # Verify that the API was called
    assert len(mock_failing_etherscan_api.calls) == 1


@pytest.mark.asyncio
async def test_get_transactions_pagination(mock_etherscan_api):
    """Test pagination in Etherscan API"""
    # First page
    response1 = await mock_etherscan_api.get_transactions(
        address="0x1111111111111111111111111111111111111111",
        start_block=12345000,
        end_block=12345999,
        page=1,
        offset=10
    )
    
    # Second page (should be empty)
    response2 = await mock_etherscan_api.get_transactions(
        address="0x1111111111111111111111111111111111111111",
        start_block=12345000,
        end_block=12345999,
        page=2,
        offset=10
    )
    
    # Verify first page has data
    assert response1["status"] == "1"
    assert len(response1["result"]) == 1
    
    # Verify second page is empty
    assert response2["status"] == "1"
    assert len(response2["result"]) == 0
    
    # Verify that the API was called twice
    assert len(mock_etherscan_api.calls) == 2
    assert mock_etherscan_api.calls[0]["page"] == 1
    assert mock_etherscan_api.calls[1]["page"] == 2


@pytest.mark.asyncio
async def test_from_field_conversion():
    """Test that 'from' field is properly converted to 'fromAddr'"""
    # Create a real API instance
    api = EtherscanTransactionsApi("fake_api_key")
    
    # Mock the response from aiohttp
    mock_response = MagicMock()
    mock_response.json.return_value = asyncio.Future()
    mock_response.json.return_value.set_result({
        "status": "1",
        "message": "OK",
        "result": [
            {
                "blockNumber": "12345678",
                "timeStamp": "1609459200",
                "hash": "0xabcdef",
                "from": "0x1111111111111111111111111111111111111111",  # Note the 'from' field
                "to": "0x2222222222222222222222222222222222222222",
                # Other fields omitted for brevity
            }
        ]
    })
    
    # Mock the ClientSession
    mock_session = MagicMock()
    mock_session.__aenter__.return_value = mock_session
    mock_session.get.return_value.__aenter__.return_value = mock_response
    
    # Patch aiohttp.ClientSession
    with patch('aiohttp.ClientSession', return_value=mock_session):
        # Call the API
        response = await api.get_transactions(
            address="0x1111111111111111111111111111111111111111",
            start_block=12345000,
            end_block=12345999,
            page=1,
            offset=10
        )
    
    # Verify that 'from' was converted to 'fromAddr'
    assert "from" not in response["result"][0]
    assert response["result"][0]["fromAddr"] == "0x1111111111111111111111111111111111111111"
