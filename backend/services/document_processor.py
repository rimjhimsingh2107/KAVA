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
import PyPDF2
from models.claim import ClaimDocument, DocumentType

class DocumentProcessor:
    def __init__(self):
        api_key = os.getenv("CLAUDE_API_KEY")
        if api_key:
            self.client = anthropic.Anthropic(api_key=api_key)
            print("✅ Claude API initialized successfully for document processing")
        else:
            self.client = None
            print("❌ WARNING: CLAUDE_API_KEY not set - document processing will fail")
        
    async def process_document(self, content: bytes, filename: str) -> ClaimDocument:
        """Process uploaded document - FIXED to handle PDFs properly"""
        
        doc_type = self._classify_document_type(filename, content)
        
        print(f"Processing document: {filename} (type: {doc_type})")
        
        # Handle different document types properly
        if content.startswith(b'%PDF'):
            # PDF file - extract text and analyze
            extracted_data = await self._process_pdf_document(content)
            print(f"PDF processed: {extracted_data.get('document_type', 'unknown')}")
        elif doc_type == DocumentType.PHOTO:
            # Image file - use Claude Vision
            extracted_data = await self._process_photo(content)
            print(f"Image processed: {extracted_data.get('damage_type', 'unknown')}")
        else:
            # Text or other files
            extracted_data = await self._process_text_document(content)
            print(f"Text document processed")
        
        confidence_score = self._calculate_confidence(extracted_data)
        
        return ClaimDocument(
            id=self._generate_document_id(),
            filename=filename,
            document_type=doc_type,
            content=base64.b64encode(content).decode('utf-8'),
            extracted_data=extracted_data,
            confidence_score=confidence_score,
            upload_timestamp=datetime.now()
        )
    
    async def _process_pdf_document(self, content: bytes) -> Dict[str, Any]:
        """Process PDF files by extracting text and analyzing with Claude"""
        
        print("Extracting text from PDF...")
        
        try:
            # Check if it's actually a PDF file
            if not content.startswith(b'%PDF'):
                print("File is not a valid PDF - treating as text")
                # Try to process as text instead
                try:
                    text_content = content.decode('utf-8')
                    return await self._analyze_text_with_claude(text_content)
                except:
                    return {
                        "document_type": "invalid_file",
                        "error": "File is not a valid PDF and cannot be decoded as text",
                        "confidence": 0.1
                    }
            
            # Extract text from PDF
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(content))
            text_content = ""
            
            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                page_text = page.extract_text()
                text_content += page_text + "\n"
            
            print(f"Extracted {len(text_content)} characters from PDF")
            
            if not text_content.strip():
                print("No text found in PDF - may be image-based PDF")
                return {
                    "document_type": "image_pdf",
                    "error": "PDF contains no extractable text - may need OCR",
                    "confidence": 0.2,
                    "suggestion": "Try converting PDF to images first"
                }
            
            # Analyze extracted text with Claude
            print("Sending extracted PDF text to Claude...")
            return await self._analyze_text_with_claude(text_content)
            
        except Exception as e:
            print(f"PDF processing failed: {e}")
            print("Attempting fallback text processing...")
            
            # Fallback: try to process as text
            try:
                text_content = content.decode('utf-8')
                return await self._analyze_text_with_claude(text_content)
            except:
                return {
                    "document_type": "pdf_error",
                    "error": f"PDF processing failed: {str(e)}",
                    "confidence": 0.1,
                    "fallback_attempted": True
                }
    
    async def _analyze_text_with_claude(self, text_content: str) -> Dict[str, Any]:
        """Analyze extracted text using Claude API"""
        
        if not self.client:
            print("⚠️ Claude API not available - cannot process document")
            return {
                "document_type": "error",
                "error": "Claude API key not configured",
                "confidence": 0.0
            }
        
        prompt = f"""Analyze this document text for insurance claim processing:

DOCUMENT TEXT:
{text_content[:3000]}

Extract key information:
1. Document type (receipt, policy, fire_report, estimate, etc.)
2. All dates found
3. All monetary amounts 
4. Names and addresses
5. Key insurance-related information
6. Any wildfire/fire damage details

Return JSON:
{{
  "document_type": "receipt|policy|fire_report|estimate|other",
  "extracted_dates": ["YYYY-MM-DD"],
  "extracted_amounts": [numbers],
  "merchant_or_agency": "string",
  "policy_number": "string or null",
  "incident_details": "string",
  "key_findings": ["list of important details"],
  "confidence": 0.8
}}"""
        
        try:
            print("Sending extracted text to Claude for analysis...")
            
            message = self.client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=1000,
                messages=[{
                    "role": "user", 
                    "content": prompt
                }]
            )
            
            response_text = message.content[0].text
            
            print("=" * 80)
            print("CLAUDE API RESPONSE - PDF TEXT ANALYSIS")
            print("=" * 80)
            print(response_text)
            print("=" * 80)
            
            # Parse JSON response
            try:
                import re
                json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
                if json_match:
                    result = json.loads(json_match.group())
                    result["processing_method"] = "claude_text_analysis"
                    return result
                else:
                    raise ValueError("No JSON found in Claude response")
            except:
                return {
                    "document_type": "text_analysis",
                    "raw_claude_response": response_text,
                    "processing_method": "claude_text_fallback",
                    "confidence": 0.6
                }
                
        except Exception as e:
            print(f"❌ Claude text analysis failed: {e}")
            print(f"❌ ERROR TYPE: {type(e).__name__}")
            print(f"❌ This means Claude API is not working properly")
            print(f"❌ Check your API credits at: https://console.anthropic.com/")
            # Return error data instead of crashing
            return {
                "document_type": "claude_api_error",
                "error": str(e),
                "error_type": type(e).__name__,
                "processing_method": "failed_claude_call",
                "confidence": 0.0,
                "message": "Claude API call failed - check credits and API key"
            }
    
    async def _process_text_document(self, content: bytes) -> Dict[str, Any]:
        """Process plain text files"""
        try:
            text_content = content.decode('utf-8')
            return await self._analyze_text_with_claude(text_content)
        except:
            try:
                text_content = content.decode('latin-1')
                return await self._analyze_text_with_claude(text_content)
            except Exception as e:
                return {
                    "document_type": "text_error",
                    "error": f"Text processing failed: {str(e)}",
                    "confidence": 0.1
                }
    
    def _classify_document_type(self, filename: str, content: bytes) -> DocumentType:
        """Classify document type based on filename and content analysis"""
        filename_lower = filename.lower()
        
        # First, classify by file extension and filename keywords
        if any(ext in filename_lower for ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp']):
            if any(word in filename_lower for word in ['receipt', 'invoice']):
                return DocumentType.RECEIPT
            else:
                return DocumentType.PHOTO
        
        # For PDFs, classify based on filename keywords
        elif content.startswith(b'%PDF'):
            if any(word in filename_lower for word in ['policy', 'insurance']):
                return DocumentType.POLICY
            elif any(word in filename_lower for word in ['receipt', 'invoice', 'estimate', 'contractor']):
                return DocumentType.RECEIPT
            elif any(word in filename_lower for word in ['fire', 'department', 'report', 'incident', 'damage', 'weather']):
                return DocumentType.DAMAGE_REPORT
            else:
                # Default to OTHER for unknown PDF types, not POLICY
                return DocumentType.OTHER
                
        elif '.txt' in filename_lower:
            if any(word in filename_lower for word in ['receipt', 'invoice']):
                return DocumentType.RECEIPT
            else:
                return DocumentType.OTHER
        
        return DocumentType.OTHER
    
    async def _process_photo(self, content: bytes) -> Dict[str, Any]:
        """Process images using Claude Vision API"""
        
        if not self.client:
            print("⚠️ Claude API not available - cannot process photo")
            return {
                "document_type": "photo",
                "error": "Claude API key not configured",
                "confidence": 0.0
            }
        
        # Detect image type
        if content.startswith(b'\x89PNG'):
            media_type = "image/png"
        elif content.startswith(b'GIF'):
            media_type = "image/gif" 
        elif content.startswith(b'\xff\xd8\xff'):
            media_type = "image/jpeg"
        else:
            media_type = "image/jpeg"  # Default
        
        base64_image = base64.b64encode(content).decode('utf-8')
        
        prompt = """Analyze this property damage photo for insurance claim:
        
        Extract: damage type, severity, affected areas, photo quality
        
        Return JSON:
        {
            "damage_type": ["fire", "smoke"],
            "severity": "severe", 
            "affected_areas": ["roof", "walls"],
            "photo_quality": "clear",
            "description": "detailed description"
        }"""
        
        try:
            message = self.client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=1000,
                messages=[{
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": media_type,
                                "data": base64_image
                            }
                        },
                        {"type": "text", "text": prompt}
                    ]
                }]
            )
            
            response_text = message.content[0].text
            
            print("=" * 80)
            print("CLAUDE API RESPONSE - IMAGE ANALYSIS")
            print("=" * 80)
            print(response_text)
            print("=" * 80)
            
            # Parse JSON
            import re
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            else:
                raise ValueError("No valid JSON found in Claude response")
                
        except Exception as e:
            print(f"❌ Claude Vision API failed: {e}")
            # NO FALLBACK - Force real Claude API usage
            raise Exception(f"Claude Vision API failed - real processing required: {e}")
    
    def _calculate_confidence(self, extracted_data: Dict[str, Any]) -> float:
        """Calculate confidence based on extraction quality"""
        if "error" in extracted_data:
            return 0.1
        
        # Count valid fields
        valid_fields = 0
        total_fields = len(extracted_data)
        
        for key, value in extracted_data.items():
            if value and value != "unknown" and value != [] and value != {}:
                valid_fields += 1
        
        return valid_fields / total_fields if total_fields > 0 else 0.5
    
    def _generate_document_id(self) -> str:
        import uuid
        return str(uuid.uuid4())
