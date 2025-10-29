import os
import json
import httpx
from typing import List, Optional
from datetime import datetime, timedelta
from models.claim import Document, DocumentType
import asyncio

class ReceiptFetcher:
    def __init__(self):
        self.knot_api_key = os.getenv("KNOT_API_KEY", "demo_key")
        self.base_url = "https://api.knotapi.com/v1"
        
    async def fetch_receipts(self, claimant_name: str, incident_date: datetime, days_back: int = 90) -> List[Document]:
        """Auto-fetch receipts for the claimant within specified timeframe"""
        try:
            # Calculate date range
            end_date = incident_date + timedelta(days=30)  # 30 days after incident
            start_date = incident_date - timedelta(days=days_back)
            
            # Mock receipt fetching (in production, integrate with Knot API)
            mock_receipts = await self._generate_mock_receipts(claimant_name, start_date, end_date)
            
            return mock_receipts
            
        except Exception as e:
            print(f"Receipt fetching failed: {e}")
            return []
    
    async def _generate_mock_receipts(self, claimant_name: str, start_date: datetime, end_date: datetime) -> List[Document]:
        """Generate mock receipts for demo purposes"""
        mock_receipts = []
        
        # Generate some realistic receipts for wildfire claim
        receipt_data = [
            {
                "merchant": "Home Depot",
                "amount": 1250.00,
                "items": ["Fire extinguisher", "Emergency supplies", "Tarps"],
                "date": start_date + timedelta(days=5)
            },
            {
                "merchant": "Target",
                "amount": 350.75,
                "items": ["Clothing", "Personal items", "Emergency kit"],
                "date": start_date + timedelta(days=7)
            },
            {
                "merchant": "Best Western Hotel",
                "amount": 890.00,
                "items": ["Emergency accommodation", "3 nights"],
                "date": start_date + timedelta(days=2)
            }
        ]
        
        for i, receipt in enumerate(receipt_data):
            doc = Document(
                id=f"auto_receipt_{i+1}",
                filename=f"{receipt['merchant']}_receipt_{receipt['date'].strftime('%Y%m%d')}.json",
                document_type=DocumentType.RECEIPT,
                extracted_data={
                    "merchant": receipt["merchant"],
                    "total_amount": receipt["amount"],
                    "items": receipt["items"],
                    "date": receipt["date"].isoformat(),
                    "auto_fetched": True
                },
                confidence_score=0.95,
                file_size=1024,
                upload_timestamp=datetime.now()
            )
            mock_receipts.append(doc)
        
        return mock_receipts
    
    async def fetch_from_knot_api(self, user_id: str, start_date: datetime, end_date: datetime) -> List[Document]:
        """Fetch receipts from Knot API (production implementation)"""
        try:
            headers = {
                "Authorization": f"Bearer {self.knot_api_key}",
                "Content-Type": "application/json"
            }
            
            params = {
                "user_id": user_id,
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "categories": ["retail", "home_improvement", "accommodation", "emergency"]
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/receipts",
                    headers=headers,
                    params=params,
                    timeout=30
                )
                
                if response.status_code == 200:
                    receipts_data = response.json()
                    return self._convert_knot_receipts_to_documents(receipts_data)
                else:
                    print(f"Knot API error: {response.status_code}")
                    return []
                    
        except Exception as e:
            print(f"Knot API fetch failed: {e}")
            return []
    
    def _convert_knot_receipts_to_documents(self, receipts_data: List[dict]) -> List[Document]:
        """Convert Knot API receipts to Document objects"""
        documents = []
        
        for i, receipt in enumerate(receipts_data.get("receipts", [])):
            doc = Document(
                id=f"knot_receipt_{receipt.get('id', i)}",
                filename=f"{receipt.get('merchant', 'unknown')}_receipt.json",
                document_type=DocumentType.RECEIPT,
                extracted_data={
                    "merchant": receipt.get("merchant"),
                    "total_amount": receipt.get("total"),
                    "items": receipt.get("items", []),
                    "date": receipt.get("date"),
                    "knot_id": receipt.get("id"),
                    "auto_fetched": True
                },
                confidence_score=0.9,
                file_size=len(json.dumps(receipt)),
                upload_timestamp=datetime.now()
            )
            documents.append(doc)
        
        return documents
