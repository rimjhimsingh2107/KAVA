# API Documentation - AI Insurance Claims Validation System

## Overview

The AI Insurance Claims Validation System provides REST API endpoints for document processing, claim validation, and proof generation. This documentation covers all available endpoints and their usage.

## Base URL
```
http://localhost:8000
```

## Authentication
Currently no authentication required for demo purposes. In production, implement proper API key authentication.

## Endpoints

### 1. Document Upload and Processing

#### `POST /api/upload-documents`

Upload and process insurance claim documents using AI vision analysis.

**Request:**
- Method: `POST`
- Content-Type: `multipart/form-data`
- Body: Form data with file uploads

**Parameters:**
- `files`: One or more files (images: JPG, PNG; documents: PDF)
- Maximum file size: 10MB per file
- Supported formats: `.jpg`, `.jpeg`, `.png`, `.pdf`

**Response:**
```json
{
  "documents": [
    {
      "id": "doc_12345",
      "filename": "damage_photo.jpg",
      "document_type": "photo",
      "extracted_data": {
        "damage_type": ["fire", "smoke"],
        "severity": "severe",
        "affected_areas": ["roof", "walls"],
        "wildfire_evidence": ["char patterns", "heat damage"],
        "description": "Severe fire damage to exterior"
      },
      "confidence_score": 0.92,
      "upload_timestamp": "2024-01-12T14:30:00Z"
    }
  ],
  "processing_time": 2.3,
  "status": "success"
}
```

**Error Responses:**
- `400`: Invalid file format or size
- `500`: Processing error

---

### 2. Claim Validation

#### `POST /api/validate-claim`

Submit a complete claim packet for AI validation and scoring.

**Request:**
```json
{
  "claim_id": "WF-2024-001",
  "policy_number": "WF-POLICY-12345",
  "claimant_name": "John Doe",
  "incident_date": "2024-01-10T00:00:00Z",
  "property_address": "123 Main St, Paradise, CA",
  "estimated_damage": 185000,
  "documents": [
    {
      "id": "doc_1",
      "filename": "damage_photo.jpg",
      "document_type": "photo",
      "extracted_data": {
        "damage_type": ["fire"],
        "severity": "severe"
      },
      "confidence_score": 0.9
    }
  ]
}
```

**Response:**
```json
{
  "claim_id": "WF-2024-001",
  "overall_score": 0.82,
  "confidence": 0.85,
  "approved": true,
  "rules_evaluated": [
    {
      "rule_id": "COMP_001",
      "description": "Property photos must show damage evidence",
      "weight": 0.15,
      "passed": true,
      "confidence": 0.9,
      "rationale": "Found 2 photos with clear damage evidence"
    }
  ],
  "missing_documents": [
    "Insurance policy documentation",
    "Additional receipts for high-value items"
  ],
  "fraud_indicators": [
    "Claim filed 365 days after incident - delayed reporting"
  ],
  "rationale": "Claim validation completed with overall score: 82.0%...",
  "timestamp": "2024-01-12T15:30:00Z"
}
```

**Validation Rules Categories:**

1. **Completeness Rules (45% weight)**
   - `COMP_001`: Property photos requirement (15%)
   - `COMP_002`: Receipt requirements for items >$100 (12%)
   - `COMP_003`: Filing within coverage period (18%)

2. **Damage Assessment (28% weight)**
   - `DAMAGE_001`: Wildfire causation evidence (20%)
   - `DAMAGE_002`: Market-rate replacement costs (8%)

3. **Documentation Quality (27% weight)**
   - `QUALITY_001`: Photo clarity and context (17%)
   - `QUALITY_002`: Document completeness variety (10%)

**Scoring:**
- Score range: 0.0 - 1.0 (0% - 100%)
- Approval threshold: 0.7 (70%)
- Confidence calibration included

---

### 3. Proof Generation

#### `POST /api/generate-proof`

Generate blockchain-anchored proof for validated claims.

**Request:**
```json
{
  "claim_id": "WF-2024-001",
  "validation_result": {
    "overall_score": 0.82,
    "approved": true,
    "timestamp": "2024-01-12T15:30:00Z"
  },
  "agent_signature": "0x1234...",
  "blockchain_network": "sepolia"
}
```

**Response:**
```json
{
  "proof_card": {
    "claim_hash": "0xabc123...",
    "agent_signature": "0x1234...",
    "validation_timestamp": "2024-01-12T15:30:00Z",
    "judge_score": 82,
    "rules_version": "v1.0",
    "blockchain_tx": "0xdef456...",
    "verification_url": "https://sepolia.etherscan.io/tx/0xdef456..."
  },
  "download_url": "/api/download-proof/WF-2024-001",
  "status": "anchored"
}
```

---

## Data Models

### ClaimPacket
```typescript
interface ClaimPacket {
  claim_id: string;
  policy_number: string;
  claimant_name: string;
  incident_date: string; // ISO 8601 format
  property_address: string;
  estimated_damage: number;
  documents: Document[];
}
```

### Document
```typescript
interface Document {
  id: string;
  filename: string;
  document_type: "photo" | "receipt" | "policy" | "other";
  content?: string; // Base64 encoded content
  extracted_data: Record<string, any>;
  confidence_score: number;
  upload_timestamp: string;
}
```

### ValidationRule
```typescript
interface ValidationRule {
  rule_id: string;
  description: string;
  weight: number;
  passed: boolean;
  confidence: number;
  rationale: string;
}
```

### ValidationResult
```typescript
interface ValidationResult {
  claim_id: string;
  overall_score: number;
  confidence: number;
  approved: boolean;
  rules_evaluated: ValidationRule[];
  missing_documents: string[];
  fraud_indicators: string[];
  rationale: string;
  timestamp: string;
}
```

## Error Handling

### Standard Error Response
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Detailed error description",
    "details": {
      "field": "specific_field_with_error",
      "reason": "validation_failure_reason"
    }
  },
  "timestamp": "2024-01-12T15:30:00Z"
}
```

### Common Error Codes
- `INVALID_FILE_FORMAT`: Unsupported file type
- `FILE_TOO_LARGE`: File exceeds size limit
- `PROCESSING_ERROR`: AI processing failed
- `VALIDATION_ERROR`: Claim validation failed
- `MISSING_REQUIRED_FIELD`: Required field not provided
- `FRAUD_DETECTED`: High fraud risk detected

## Rate Limits

- Document upload: 10 requests/minute per IP
- Claim validation: 5 requests/minute per IP
- Proof generation: 3 requests/minute per IP

## Integration Examples

### Python Example
```python
import requests
import json

# Upload documents
files = {'files': open('damage_photo.jpg', 'rb')}
response = requests.post('http://localhost:8000/api/upload-documents', files=files)
documents = response.json()['documents']

# Validate claim
claim_data = {
    "claim_id": "WF-2024-001",
    "policy_number": "WF-POLICY-12345",
    "claimant_name": "John Doe",
    "incident_date": "2024-01-10T00:00:00Z",
    "property_address": "123 Main St",
    "estimated_damage": 185000,
    "documents": documents
}

validation = requests.post(
    'http://localhost:8000/api/validate-claim',
    json=claim_data
)
result = validation.json()
print(f"Claim score: {result['overall_score']*100:.1f}%")
```

### JavaScript Example
```javascript
// Upload documents
const formData = new FormData();
formData.append('files', fileInput.files[0]);

const uploadResponse = await fetch('/api/upload-documents', {
  method: 'POST',
  body: formData
});
const { documents } = await uploadResponse.json();

// Validate claim
const claimData = {
  claim_id: 'WF-2024-001',
  policy_number: 'WF-POLICY-12345',
  claimant_name: 'John Doe',
  incident_date: '2024-01-10T00:00:00Z',
  property_address: '123 Main St',
  estimated_damage: 185000,
  documents: documents
};

const validationResponse = await fetch('/api/validate-claim', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify(claimData)
});

const result = await validationResponse.json();
console.log(`Claim score: ${(result.overall_score * 100).toFixed(1)}%`);
```

## Security Considerations

1. **Input Validation**: All inputs are validated and sanitized
2. **File Scanning**: Uploaded files are scanned for malware
3. **Rate Limiting**: API calls are rate-limited to prevent abuse
4. **Data Privacy**: Sensitive data is encrypted at rest
5. **Audit Logging**: All API calls are logged for audit purposes

## EigenCloud TEE Integration

When EigenCloud TEE is available, validation requests are automatically routed through the secure execution environment:

- **Secure Evaluation**: Claims processed in tamper-proof environment
- **Cryptographic Attestation**: Results include attestation hash
- **Fallback Logic**: Automatic fallback to local validation if TEE unavailable

TEE Response includes additional fields:
```json
{
  "tee_attestation": {
    "attestation_hash": "d7732b5d16d0925c...",
    "evaluator_address": "0xc557eec878dfd852...",
    "secure_enclave": true
  }
}
```

## Performance Metrics

- **Document Processing**: 2-3 seconds per document
- **AI Validation**: 5-10 seconds for complete evaluation
- **Proof Generation**: 15-30 seconds (blockchain dependent)
- **Concurrent Requests**: Up to 10 simultaneous validations

## Support

For technical support and integration assistance:
- GitHub Issues: [Repository Issues](https://github.com/your-repo/issues)
- Documentation: This file and README.md
- Demo Environment: http://localhost:3001
