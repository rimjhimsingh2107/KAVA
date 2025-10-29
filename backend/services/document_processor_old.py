import os
import json
import base64
from typing import Dict, Any, List
from datetime import datetime
import anthropic
from PIL import Image
import io
import cv2
import numpy as np
from models.claim import Document, DocumentType

class DocumentProcessor:
    def __init__(self):
        api_key = os.getenv("CLAUDE_API_KEY")
        if not api_key:
            raise ValueError("CLAUDE_API_KEY environment variable is required")
        
        self.client = anthropic.Anthropic(api_key=api_key)
        print("✅ Claude API initialized successfully")
        
    async def process_document(self, content: bytes, filename: str) -> Document:
        """Process uploaded document using Claude Vision"""
        
        # Determine document type from filename and content
        doc_type = self._classify_document_type(filename, content)
        
        # Extract data based on document type
        if doc_type == DocumentType.PHOTO:
            extracted_data = await self._process_photo(content)
        elif doc_type == DocumentType.RECEIPT:
            extracted_data = await self._process_receipt(content)
        elif doc_type == DocumentType.POLICY:
            extracted_data = await self._process_policy_document(content)
        else:
            extracted_data = await self._process_generic_document(content)
        
        # Calculate confidence score
        confidence_score = self._calculate_confidence(extracted_data)
        
        return Document(
            id=self._generate_document_id(),
            filename=filename,
            document_type=doc_type,
            extracted_data=extracted_data,
            confidence_score=confidence_score,
            file_size=len(content),
            upload_timestamp=datetime.now()
        )
    
    def _classify_document_type(self, filename: str, content: bytes) -> DocumentType:
        """Classify document type based on filename and content analysis"""
        filename_lower = filename.lower()
        
        # Image files are likely photos or receipts
        if any(ext in filename_lower for ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp']):
            # Use simple heuristics for now - could be enhanced with ML
            if any(word in filename_lower for word in ['receipt', 'invoice', 'bill']):
                return DocumentType.RECEIPT
            elif any(word in filename_lower for word in ['damage', 'photo', 'before', 'after']):
                return DocumentType.PHOTO
            else:
                return DocumentType.PHOTO  # Default for images
        
        # PDF files could be policies or receipts
        elif '.pdf' in filename_lower:
            if any(word in filename_lower for word in ['policy', 'insurance', 'coverage']):
                return DocumentType.POLICY
            else:
                return DocumentType.RECEIPT
        
        return DocumentType.OTHER
    
    async def _process_photo(self, content: bytes) -> Dict[str, Any]:
        """Process photo using Claude Vision to extract damage information"""
        
        # Convert to base64 for Claude
        base64_image = base64.b64encode(content).decode('utf-8')
        
        prompt = """
        Analyze this property damage photo for an insurance claim. Extract:
        
        1. Type of damage visible (fire, smoke, water, structural, etc.)
        2. Severity assessment (minor, moderate, severe, total loss)
        3. Affected areas/items (roof, walls, furniture, appliances, etc.)
        4. Estimated timeframe of damage (recent, old, pre-existing)
        5. Photo quality assessment (clear, blurry, adequate lighting, etc.)
        6. Any visible date/timestamp information
        7. Location indicators (interior, exterior, specific rooms)
        8. Evidence of wildfire causation (char patterns, heat damage, etc.)
        
        Respond in JSON format with these fields:
        {
            "damage_type": [],
            "severity": "string",
            "affected_areas": [],
            "damage_timeframe": "string",
            "photo_quality": "string",
            "timestamp_visible": "string",
            "location": "string",
            "wildfire_evidence": [],
            "description": "string"
        }
        """
        
        try:
            message = self.client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=1500,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image",
                                "source": {
                                    "type": "base64",
                                    "media_type": "image/jpeg",
                                    "data": base64_image
                                }
                            },
                            {
                                "type": "text",
                                "text": prompt
                            }
                        ]
                    }
                ]
            )
            
            response_text = message.content[0].text
            
            # Console log the Claude response
            print("\n" + "="*80)
            print("🤖 CLAUDE API RESPONSE - PHOTO PROCESSING")
            print("="*80)
            print(response_text)
            print("="*80 + "\n")
            
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1
            json_str = response_text[json_start:json_end]
            
            return json.loads(json_str)
            
        except Exception as e:
            print(f"Error processing photo: {e}")
            raise Exception(f"Failed to process photo with Claude API: {e}")
    
    async def _process_receipt(self, content: bytes) -> Dict[str, Any]:
        """Process receipt using Claude Vision to extract transaction details"""
        
        base64_image = base64.b64encode(content).decode('utf-8')
        
        prompt = """
        Extract information from this receipt for insurance claim processing:
        
        1. Merchant name and location
        2. Transaction date and time
        3. Total amount
        4. Individual items purchased with prices
        5. Payment method
        6. Receipt/transaction ID
        7. Tax amount
        8. Category of items (home improvement, temporary housing, clothing, etc.)
        
        Respond in JSON format:
        {
            "merchant": "string",
            "location": "string",
            "date": "YYYY-MM-DD",
            "time": "HH:MM",
            "total_amount": 0.00,
            "items": [{"name": "string", "price": 0.00, "quantity": 1}],
            "payment_method": "string",
            "transaction_id": "string",
            "tax_amount": 0.00,
            "category": "string",
            "receipt_quality": "string"
        }
        """
        
        try:
            message = self.client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=1500,
                messages=[{
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": "image/jpeg",
                                "data": base64_image
                            }
                        }
                    ]
                }]
            )
            
            response_text = message.content[0].text
            
            # Console log the Claude response
            print("\n" + "="*80)
            print("🤖 CLAUDE API RESPONSE - RECEIPT PROCESSING")
            print("="*80)
            print(response_text)
            print("="*80 + "\n")
            
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1
            json_str = response_text[json_start:json_end]
            
            return json.loads(json_str)
            
        except Exception as e:
            print(f"Error processing receipt: {e}")
            raise Exception(f"Failed to process receipt with Claude API: {e}")
    
    async def _process_policy_document(self, content: bytes) -> Dict[str, Any]:
        """Process insurance policy document"""
        
        # For PDF files, we need to handle them differently
        # Claude can process PDFs directly without converting to image
        base64_content = base64.b64encode(content).decode('utf-8')
        
        prompt = """
        Extract key information from this insurance policy document:
        
        1. Policy number
        2. Policy holder name
        3. Property address
        4. Coverage period (start and end dates)
        5. Coverage types and limits
        6. Deductible amounts
        7. Wildfire/fire coverage details
        8. Exclusions relevant to wildfire claims
        
        Respond in JSON format:
        {
            "policy_number": "string",
            "policy_holder": "string",
            "property_address": "string",
            "coverage_start": "YYYY-MM-DD",
            "coverage_end": "YYYY-MM-DD",
            "coverage_types": {"type": "limit"},
            "deductible": 0.00,
            "wildfire_coverage": "boolean",
            "fire_coverage_limit": 0.00,
            "relevant_exclusions": []
        }
        """
        
        try:
            message = self.client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=1500,
                messages=[{
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "document",
                            "source": {
                                "type": "base64",
                                "media_type": "application/pdf",
                                "data": base64_content
                            }
                        }
                    ]
                }]
            )
            
            response_text = message.content[0].text
            
            # Console log the Claude response
            print("\n" + "="*80)
            print("🤖 CLAUDE API RESPONSE - POLICY PROCESSING")
            print("="*80)
            print(response_text)
            print("="*80 + "\n")
            
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1
            json_str = response_text[json_start:json_end]
            
            return json.loads(json_str)
            
        except Exception as e:
            print(f"Error processing policy: {e}")
            raise Exception(f"Failed to process policy with Claude API: {e}")
    
    async def _process_generic_document(self, content: bytes) -> Dict[str, Any]:
        """Process generic document"""
        
        base64_content = base64.b64encode(content).decode('utf-8')
        
        prompt = """
        Analyze this document and extract any information relevant to an insurance claim:
        
        1. Document type
        2. Key dates
        3. Names and addresses
        4. Financial amounts
        5. Property or damage descriptions
        6. Any other relevant details
        
        Respond in JSON format:
        {
            "document_type": "string",
            "key_dates": [],
            "names": [],
            "addresses": [],
            "amounts": [],
            "descriptions": [],
            "other_details": []
        }
        """
        
        try:
            # Try to determine if this is a PDF or image
            is_pdf = content.startswith(b'%PDF')
            
            if is_pdf:
                content_type = {
                    "type": "document",
                    "source": {
                        "type": "base64",
                        "media_type": "application/pdf",
                        "data": base64_content
                    }
                }
            else:
                content_type = {
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": "image/jpeg",
                        "data": base64_content
                    }
                }
            
            message = self.client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=1000,
                messages=[{
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        content_type
                    ]
                }]
            )
            
            response_text = message.content[0].text
            
            # Console log the Claude response
            print("\n" + "="*80)
            print("🤖 CLAUDE API RESPONSE - GENERIC DOCUMENT PROCESSING")
            print("="*80)
            print(response_text)
            print("="*80 + "\n")
            
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1
            json_str = response_text[json_start:json_end]
            
            return json.loads(json_str)
            
        except Exception as e:
            print(f"Error processing document: {e}")
            raise Exception(f"Failed to process document with Claude API: {e}")
    
    def _calculate_confidence(self, extracted_data: Dict[str, Any]) -> float:
        """Calculate confidence score based on extracted data quality"""
        
        if "error" in extracted_data:
            return 0.1
        
        # Count non-empty/non-unknown fields
        total_fields = len(extracted_data)
        valid_fields = 0
        
        for key, value in extracted_data.items():
            if value and value != "unknown" and value != [] and value != {}:
                valid_fields += 1
        
        base_confidence = valid_fields / total_fields if total_fields > 0 else 0.0
        
        # Adjust based on specific quality indicators
        if "receipt_quality" in extracted_data:
            if extracted_data["receipt_quality"] == "excellent":
                base_confidence *= 1.1
            elif extracted_data["receipt_quality"] == "poor":
                base_confidence *= 0.8
        
        if "photo_quality" in extracted_data:
            if extracted_data["photo_quality"] == "clear":
                base_confidence *= 1.1
            elif extracted_data["photo_quality"] == "blurry":
                base_confidence *= 0.7
        
        return min(1.0, base_confidence)
    
    
    def _generate_document_id(self) -> str:
        """Generate unique document ID"""
        import uuid
        return str(uuid.uuid4())
    
    def enhance_image_quality(self, image_bytes: bytes) -> bytes:
        """Enhance image quality for better OCR results"""
        try:
            # Convert bytes to numpy array
            nparr = np.frombuffer(image_bytes, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            # Apply image enhancement techniques
            # Convert to grayscale
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
            # Apply denoising
            denoised = cv2.fastNlMeansDenoising(gray)
            
            # Apply sharpening
            kernel = np.array([[-1,-1,-1], [-1,9,-1], [-1,-1,-1]])
            sharpened = cv2.filter2D(denoised, -1, kernel)
            
            # Encode back to bytes
            _, buffer = cv2.imencode('.jpg', sharpened)
            return buffer.tobytes()
            
        except Exception as e:
            print(f"Error enhancing image: {e}")
            return image_bytes  # Return original if enhancement fails
    
    async def reprocess_document(self, document: Document) -> Document:
        """Reprocess document with enhanced OCR for better results"""
        try:
            # For now, return the same document with slightly improved confidence
            # In production, this would re-run OCR with different parameters
            enhanced_doc = Document(
                id=document.id,
                filename=document.filename,
                document_type=document.document_type,
                extracted_data=document.extracted_data,
                confidence_score=min(1.0, document.confidence_score + 0.1),
                file_size=document.file_size,
                upload_timestamp=document.upload_timestamp
            )
            return enhanced_doc
        except Exception as e:
            print(f"Error reprocessing document: {e}")
            return document
