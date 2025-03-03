# Tres Project - Ethereum Transaction Sync API

## Overview

This project provides an API to synchronize and query Ethereum transactions for specific wallet addresses within defined block ranges. It uses the Etherscan API to fetch transaction data and stores it in a PostgreSQL database.

## Setup Instructions

1. Create and activate virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Start PostgreSQL using Docker Compose:
   ```bash
   # Make the script executable first (if needed)
   chmod +x start_db.sh
   
   # Start the PostgreSQL container
   ./start_db.sh
   ```
   
   To stop the PostgreSQL container:
   ```bash
   ./stop_db.sh
   ```

4. Create a `.env` file based on `.env.example` and add your Etherscan API key:
   ```
   # Database connection settings
   DB_NAME=tres_db
   DB_USER=postgres
   DB_PASSWORD=postgres
   DB_HOST=localhost
   DB_PORT=5432
   
   # Etherscan API key
   ETHERSCAN_API_KEY=your_etherscan_api_key_here
   ```

5. Run the main script to create tables and start the API server:
   ```bash
   python main.py
   ```

## API Endpoints

### 1. Start Transaction Synchronization

**Endpoint:** `POST /start_sync`

**Request Body:**
```json
{
  "address": "0x613700baf1481f3781a6b3ec9e44a4585f89dfbc",
  "start_block": 12345678,
  "end_block": 12345700
}
```

**Response:**
```json
{
  "message": "Sync completed for wallet 0x613700baf1481f3781a6b3ec9e44a4585f89dfbc"
}
```

### 2. Get Transactions for a Wallet

**Endpoint:** `GET /transactions?address=0x613700baf1481f3781a6b3ec9e44a4585f89dfbc`

**Response:**
```json
{
  "transactions": [
    {
      "block_number": 12345678,
      "time_stamp": "2022-01-01T12:00:00",
      "hash": "0xabcdef...",
      "from_addr": "0x123...",
      "to": "0x456...",
      "value": "1000000000000000000",
      "gas": "21000",
      "gas_price": "50000000000",
      "is_error": false,
      "function_name": "transfer(address,uint256)"
    }
  ],
  "block_ranges": [
    {
      "start_block": 12345678,
      "end_block": 12345700
    }
  ]
}
```

### 3. Health Check

**Endpoint:** `GET /health`

**Response:**
```json
{
  "status": "ok"
}
```

## Development

- The project uses FastAPI for the API server
- Peewee is used as the ORM for database operations
- Database configuration is in `tres/database.py`
- Models are defined in `tres/models.py`
- API endpoints are defined in `tres/server.py`
- Transaction synchronization logic is in `tres/sync.py`
- Etherscan API client is in `tres/etherscan.py`

## Testing

The project includes a comprehensive test suite using pytest:

```bash
# Run all tests
python -m pytest tests/

# Run specific test files
python -m pytest tests/test_etherscan.py
python -m pytest tests/test_sync.py
python -m pytest tests/test_server.py

# Run with verbose output
python -m pytest tests/ -v
```

The tests use:
- SQLite in-memory database for testing database operations
- Mock Etherscan API for testing API interactions
- FastAPI TestClient for testing HTTP endpoints

## Database Configuration

The project includes Docker Compose configuration for PostgreSQL:

- The database settings are automatically read from your `.env` file
- The PostgreSQL container is configured to use the values from `.env`
- Data is persisted in a Docker volume named `postgres_data`
- The container exposes PostgreSQL on the port specified in `.env` (default: 5432)

### Docker Commands

Start the PostgreSQL container:
```bash
docker compose up -d postgres
```

Stop the PostgreSQL container:
```bash
docker compose down
```

View PostgreSQL logs:
```bash
docker compose logs postgres
```

Connect to PostgreSQL using psql (from inside the container):
```bash
docker compose exec postgres psql -U postgres -d tres_db
```

VS Code debugging is configured and ready to use.
