from sqlalchemy import create_engine, Column, String, DateTime, Float, Boolean, Text, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from datetime import datetime
import os

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./claims.db")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class ClaimRecord(Base):
    __tablename__ = "claims"
    
    claim_id = Column(String, primary_key=True, index=True)
    policy_number = Column(String, index=True)
    claimant_name = Column(String)
    incident_date = Column(DateTime)
    property_address = Column(String)
    estimated_damage = Column(Float)
    status = Column(String, default="processing")
    documents = Column(JSON)
    validation_result = Column(JSON)
    proof_card = Column(JSON)
    blockchain_tx_hash = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# Create tables
Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
