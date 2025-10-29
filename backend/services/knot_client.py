import os
import requests
import json
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from models.claim import Receipt

class KnotClient:
    def __init__(self):
        self.api_key = os.getenv("KNOT_API_KEY")
        self.base_url = "https://api.knotapi.com/v1"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    async def find_receipts(self, claim_data: Dict[str, Any]) -> List[Receipt]:
        """Find receipts using Knot TransactionLink based on claim data"""
        
        # Extract search parameters from claim data
        incident_date = datetime.fromisoformat(claim_data.get("incident_date", ""))
        property_address = claim_data.get("property_address", "")
        claimant_name = claim_data.get("claimant_name", "")
        
        # Define search timeframe (incident date + 90 days for recovery purchases)
        start_date = incident_date
        end_date = incident_date + timedelta(days=90)
        
        # Search for relevant transactions
        receipts = []
        
        # Search different merchant categories relevant to wildfire recovery
        categories = [
            "home_improvement",
            "hardware_stores", 
            "hotels_lodging",
            "clothing_stores",
            "electronics",
            "furniture",
            "grocery_stores"
        ]
        
        for category in categories:
            category_receipts = await self._search_by_category(
                category, start_date, end_date, property_address
            )
            receipts.extend(category_receipts)
        
        # Search specific merchants commonly used for disaster recovery
        disaster_merchants = [
            "Home Depot",
            "Lowes", 
            "Amazon",
            "Walmart",
            "Target",
            "Best Buy",
            "Costco"
        ]
        
        for merchant in disaster_merchants:
            merchant_receipts = await self._search_by_merchant(
                merchant, start_date, end_date
            )
            receipts.extend(merchant_receipts)
        
        # Remove duplicates and filter relevant items
        unique_receipts = self._deduplicate_receipts(receipts)
        relevant_receipts = self._filter_relevant_receipts(unique_receipts, claim_data)
        
        return relevant_receipts
    
    async def _search_by_category(self, category: str, start_date: datetime, 
                                end_date: datetime, location: str) -> List[Receipt]:
        """Search transactions by merchant category"""
        
        payload = {
            "filters": {
                "merchant_category": category,
                "date_range": {
                    "start": start_date.isoformat(),
                    "end": end_date.isoformat()
                },
                "location_radius": {
                    "address": location,
                    "radius_miles": 50
                }
            },
            "include_receipt_data": True,
            "limit": 100
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/transactions/search",
                headers=self.headers,
                json=payload
            )
            
            if response.status_code == 200:
                transactions = response.json().get("transactions", [])
                return [self._convert_transaction_to_receipt(tx) for tx in transactions]
            else:
                print(f"Error searching category {category}: {response.status_code}")
                return []
                
        except Exception as e:
            print(f"Error in category search: {e}")
            return []
    
    async def _search_by_merchant(self, merchant: str, start_date: datetime, 
                                end_date: datetime) -> List[Receipt]:
        """Search transactions by specific merchant"""
        
        payload = {
            "filters": {
                "merchant_name": merchant,
                "date_range": {
                    "start": start_date.isoformat(),
                    "end": end_date.isoformat()
                }
            },
            "include_receipt_data": True,
            "limit": 50
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/transactions/search",
                headers=self.headers,
                json=payload
            )
            
            if response.status_code == 200:
                transactions = response.json().get("transactions", [])
                return [self._convert_transaction_to_receipt(tx) for tx in transactions]
            else:
                print(f"Error searching merchant {merchant}: {response.status_code}")
                return []
                
        except Exception as e:
            print(f"Error in merchant search: {e}")
            return []
    
    def _convert_transaction_to_receipt(self, transaction: Dict[str, Any]) -> Receipt:
        """Convert Knot transaction data to Receipt model"""
        
        # Extract items from receipt data
        items = []
        receipt_data = transaction.get("receipt_data", {})
        
        if "line_items" in receipt_data:
            for item in receipt_data["line_items"]:
                items.append(item.get("description", "Unknown item"))
        
        # Determine category based on merchant and items
        category = self._categorize_purchase(
            transaction.get("merchant", {}).get("name", ""),
            items
        )
        
        return Receipt(
            id=transaction.get("id", ""),
            merchant=transaction.get("merchant", {}).get("name", "Unknown"),
            date=datetime.fromisoformat(transaction.get("date", "")),
            amount=float(transaction.get("amount", 0.0)),
            items=items,
            category=category,
            location=transaction.get("merchant", {}).get("location", ""),
            transaction_id=transaction.get("transaction_id", ""),
            confidence=0.8  # Initial confidence, will be validated by AI
        )
    
    def _categorize_purchase(self, merchant: str, items: List[str]) -> str:
        """Categorize purchase based on merchant and items"""
        
        merchant_lower = merchant.lower()
        items_text = " ".join(items).lower()
        
        # Home improvement/repair
        if any(keyword in merchant_lower for keyword in ["home depot", "lowes", "hardware"]):
            return "home_improvement"
        
        if any(keyword in items_text for keyword in ["lumber", "paint", "tools", "roofing", "drywall"]):
            return "home_improvement"
        
        # Temporary housing
        if any(keyword in merchant_lower for keyword in ["hotel", "motel", "inn", "airbnb"]):
            return "temporary_housing"
        
        # Clothing replacement
        if any(keyword in merchant_lower for keyword in ["clothing", "apparel", "fashion"]):
            return "clothing"
        
        if any(keyword in items_text for keyword in ["shirt", "pants", "shoes", "jacket"]):
            return "clothing"
        
        # Electronics replacement
        if any(keyword in merchant_lower for keyword in ["best buy", "electronics", "apple"]):
            return "electronics"
        
        if any(keyword in items_text for keyword in ["laptop", "phone", "tv", "computer"]):
            return "electronics"
        
        # Furniture
        if any(keyword in items_text for keyword in ["furniture", "chair", "table", "bed", "sofa"]):
            return "furniture"
        
        # Food/necessities
        if any(keyword in merchant_lower for keyword in ["grocery", "supermarket", "walmart", "target"]):
            return "necessities"
        
        return "other"
    
    def _deduplicate_receipts(self, receipts: List[Receipt]) -> List[Receipt]:
        """Remove duplicate receipts based on transaction ID and amount"""
        seen = set()
        unique_receipts = []
        
        for receipt in receipts:
            # Create unique key from transaction_id, merchant, date, and amount
            key = f"{receipt.transaction_id}_{receipt.merchant}_{receipt.date}_{receipt.amount}"
            
            if key not in seen:
                seen.add(key)
                unique_receipts.append(receipt)
        
        return unique_receipts
    
    def _filter_relevant_receipts(self, receipts: List[Receipt], 
                                claim_data: Dict[str, Any]) -> List[Receipt]:
        """Filter receipts to only include those relevant to wildfire recovery"""
        
        relevant_receipts = []
        
        # Keywords that indicate wildfire recovery purchases
        recovery_keywords = [
            # Home repair
            "lumber", "wood", "plywood", "drywall", "paint", "primer", "roofing", 
            "shingles", "insulation", "electrical", "plumbing", "tools", "hardware",
            "generator", "extension cord", "tarp", "plastic sheeting",
            
            # Cleaning supplies
            "cleaning", "detergent", "bleach", "disinfectant", "vacuum", "mop",
            "trash bags", "gloves", "masks",
            
            # Temporary housing items
            "hotel", "motel", "lodging", "rental", "airbnb",
            
            # Clothing replacement
            "clothing", "shirt", "pants", "shoes", "underwear", "socks", "jacket",
            
            # Electronics replacement
            "laptop", "computer", "phone", "tablet", "tv", "radio", "charger",
            
            # Furniture replacement
            "furniture", "bed", "mattress", "chair", "table", "dresser", "couch",
            
            # Kitchen items
            "cookware", "dishes", "utensils", "microwave", "refrigerator",
            
            # Personal care
            "toiletries", "toothbrush", "shampoo", "soap", "medication"
        ]
        
        for receipt in receipts:
            # Check if any items contain recovery keywords
            items_text = " ".join(receipt.items).lower()
            merchant_lower = receipt.merchant.lower()
            
            is_relevant = False
            
            # Check items for recovery keywords
            for keyword in recovery_keywords:
                if keyword in items_text:
                    is_relevant = True
                    break
            
            # Check merchant categories
            if receipt.category in ["home_improvement", "temporary_housing", "clothing", "electronics"]:
                is_relevant = True
            
            # Check for disaster recovery merchants
            disaster_merchants = ["home depot", "lowes", "amazon", "walmart", "target"]
            if any(merchant in merchant_lower for merchant in disaster_merchants):
                is_relevant = True
            
            if is_relevant:
                relevant_receipts.append(receipt)
        
        return relevant_receipts
    
    async def get_receipt_details(self, transaction_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed receipt information for a specific transaction"""
        
        try:
            response = requests.get(
                f"{self.base_url}/transactions/{transaction_id}/receipt",
                headers=self.headers
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Error getting receipt details: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"Error fetching receipt details: {e}")
            return None
    
    async def search_by_keywords(self, keywords: List[str], start_date: datetime, 
                               end_date: datetime) -> List[Receipt]:
        """Search for transactions containing specific keywords"""
        
        payload = {
            "filters": {
                "keywords": keywords,
                "date_range": {
                    "start": start_date.isoformat(),
                    "end": end_date.isoformat()
                }
            },
            "include_receipt_data": True,
            "limit": 100
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/transactions/search",
                headers=self.headers,
                json=payload
            )
            
            if response.status_code == 200:
                transactions = response.json().get("transactions", [])
                return [self._convert_transaction_to_receipt(tx) for tx in transactions]
            else:
                print(f"Error in keyword search: {response.status_code}")
                return []
                
        except Exception as e:
            print(f"Error in keyword search: {e}")
            return []
