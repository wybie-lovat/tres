import datetime
import logging
from peewee import Model, AutoField, CharField, DateTimeField, TextField, IntegerField, ForeignKeyField, BooleanField, Check, CompositeKey
from .database import db

# Configure logging
logger = logging.getLogger(__name__)

class BaseModel(Model):
    class Meta:
        database = db

class Wallet(BaseModel):
    id = AutoField(primary_key=True)
    address = CharField(unique=True, index=True, max_length=42)
    created_at = DateTimeField(default=datetime.datetime.now)
    updated_at = DateTimeField(default=datetime.datetime.now)
    
    def save(self, *args, **kwargs):
        self.updated_at = datetime.datetime.now()
        return super(Wallet, self).save(*args, **kwargs)
    
    def __str__(self):
        return f"Wallet({self.address})"
    
    @classmethod
    def get_by_address(cls, address):
        """Get a wallet by its address, case-insensitive."""
        try:
            return cls.get(cls.address == address)
        except cls.DoesNotExist:
            logger.info(f"Wallet not found: {address}")
            return None

class BlockRange(BaseModel):
    id = AutoField(primary_key=True)
    wallet = ForeignKeyField(Wallet, backref='block_ranges')
    start_block = IntegerField()
    end_block = IntegerField()
    transaction_count = IntegerField(default=0)
    created_at = DateTimeField(default=datetime.datetime.now)
    updated_at = DateTimeField(default=datetime.datetime.now)
    
    class Meta:
        # Add a constraint to ensure end_block is greater than or equal to start_block
        constraints = [Check('end_block >= start_block')]
        # Add a unique constraint for wallet + block range to prevent duplicates
        indexes = [
            (('wallet', 'start_block', 'end_block'), True)
        ]
    
    def save(self, *args, **kwargs):
        self.updated_at = datetime.datetime.now()
        return super(BlockRange, self).save(*args, **kwargs)
    
    def __str__(self):
        return f"BlockRange({self.wallet.address}, {self.start_block}-{self.end_block})"
    
    @classmethod
    def find_overlapping(cls, wallet, start_block, end_block):
        """Find block ranges that overlap with the given range."""
        return cls.select().where(
            (cls.wallet == wallet) &
            (cls.end_block >= start_block) &
            (cls.start_block <= end_block)
        )

class Transaction(BaseModel):
    id = AutoField(primary_key=True)
    wallet = ForeignKeyField(Wallet, backref='transactions')
    block_number = IntegerField(index=True)
    time_stamp = DateTimeField()
    hash = CharField(unique=True, index=True, max_length=66)  # 0x + 64 hex chars
    nonce = CharField()
    block_hash = CharField(max_length=66)
    transaction_index = CharField()
    from_addr = CharField(index=True, max_length=42)  # Ethereum address length
    to = CharField(index=True, null=True, max_length=42)  # Ethereum address length
    value = CharField()
    gas = CharField()
    gas_price = CharField()
    is_error = BooleanField(default=False)
    txreceipt_status = CharField(null=True)
    input = TextField()
    contract_address = CharField(null=True, max_length=42)  # Ethereum address length
    cumulative_gas_used = CharField()
    gas_used = CharField()
    confirmations = CharField()
    method_id = CharField(null=True)
    function_name = TextField(null=True)
    created_at = DateTimeField(default=datetime.datetime.now)
    updated_at = DateTimeField(default=datetime.datetime.now)
    
    class Meta:
        # Add indexes for common query patterns
        indexes = [
            (('wallet', 'block_number'), False),  # For ordering by block number
            (('wallet', 'time_stamp'), False),     # For ordering by timestamp
            (('wallet', 'is_error'), False)        # For filtering errors
        ]
    
    def save(self, *args, **kwargs):
        self.updated_at = datetime.datetime.now()
        return super(Transaction, self).save(*args, **kwargs)
    
    def __str__(self):
        return f"Transaction({self.hash[:10]}...)"
    
    @property
    def eth_value(self):
        """Return the transaction value in ETH."""
        try:
            # Convert wei to ETH (1 ETH = 10^18 wei)
            return float(self.value) / 10**18
        except (ValueError, TypeError):
            return 0.0
    
    @classmethod
    def get_by_hash(cls, tx_hash):
        """Get a transaction by its hash."""
        try:
            return cls.get(cls.hash == tx_hash)
        except cls.DoesNotExist:
            return None
