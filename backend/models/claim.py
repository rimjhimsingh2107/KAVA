from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

class DocumentType(str, Enum):
    POLICY = "policy"
    RECEIPT = "receipt"
    PHOTO = "photo"
    DAMAGE_REPORT = "damage_report"
    OTHER = "other"

class Document(BaseModel):
    id: str
    filename: str
    document_type: DocumentType
    extracted_data: Dict[str, Any]
    confidence_score: float
    file_size: int
    upload_timestamp: datetime

class ClaimDocument(BaseModel):
    id: str
    filename: str
    document_type: DocumentType
    content: str
    extracted_data: Dict[str, Any]
    confidence_score: float
    upload_timestamp: datetime

class ClaimPacket(BaseModel):
    claim_id: str
    policy_number: str
    claimant_name: str
    incident_date: datetime
    property_address: str
    documents: List[Document]
    estimated_damage: Optional[float] = None
    created_at: datetime = datetime.now()

class ValidationRule(BaseModel):
    rule_id: str
    description: str
    weight: float
    passed: bool
    confidence: float
    rationale: str

class ClaimValidation(BaseModel):
    claim_id: str
    overall_score: float
    confidence: float
    approved: bool
    rules_evaluated: List[ValidationRule]
    missing_documents: List[str]
    fraud_indicators: List[str]
    rationale: str
    timestamp: datetime = datetime.now()

class ProofCard(BaseModel):
    claim_hash: str
    agent_signature: str
    timestamp: int
    judge_score: float
    validation_rules_version: str
    blockchain_tx_hash: Optional[str] = None

class Receipt(BaseModel):
    id: str
    merchant: str
    date: datetime
    amount: float
    items: List[str]
    category: str
    location: Optional[str] = None
    transaction_id: str
    confidence: float
