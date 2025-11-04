import os
import json
import hashlib
import time
from typing import Dict, Any, Optional
from web3 import Web3
from eth_account import Account
from models.claim import ClaimPacket, ClaimValidation, ProofCard
import logging

class BlockchainService:
    def __init__(self):
        # Connect to Sepolia testnet
        self.w3 = Web3(Web3.HTTPProvider(os.getenv("SEPOLIA_RPC_URL", "https://sepolia.infura.io/v3/YOUR_PROJECT_ID")))
        
        # Load private key for signing
        self.private_key = os.getenv("PRIVATE_KEY")
        if self.private_key:
            self.account = Account.from_key(self.private_key)
        else:
            # Generate a new account if no private key provided
            self.account = Account.create()
            print(f"Generated new account: {self.account.address}")
            print(f"Private key: {self.account.key.hex()}")
        
        # Smart contract details
        self.contract_address = os.getenv("CONTRACT_ADDRESS")
        self.contract_abi = self._get_contract_abi()
        
        if self.contract_address and self.w3.is_connected():
            self.contract = self.w3.eth.contract(
                address=self.contract_address,
                abi=self.contract_abi
            )
        else:
            self.contract = None
            print("Warning: Blockchain connection not established")
    
    def _get_contract_abi(self) -> list:
        """Get the ABI for the ClaimRegistry smart contract"""
        return [
            {
                "inputs": [
                    {"name": "_claimHash", "type": "bytes32"},
                    {"name": "_signature", "type": "bytes"},
                    {"name": "_score", "type": "uint256"},
                    {"name": "_timestamp", "type": "uint256"}
                ],
                "name": "registerClaim",
                "outputs": [],
                "stateMutability": "nonpayable",
                "type": "function"
            },
            {
                "inputs": [{"name": "", "type": "bytes32"}],
                "name": "claims",
                "outputs": [
                    {"name": "claimHash", "type": "bytes32"},
                    {"name": "agentSignature", "type": "bytes"},
                    {"name": "timestamp", "type": "uint256"},
                    {"name": "score", "type": "uint256"},
                    {"name": "isValid", "type": "bool"}
                ],
                "stateMutability": "view",
                "type": "function"
            },
            {
                "inputs": [{"name": "_claimHash", "type": "bytes32"}],
                "name": "verifyClaim",
                "outputs": [{"name": "", "type": "bool"}],
                "stateMutability": "view",
                "type": "function"
            }
        ]
    
    async def generate_proof_card(self, claim_packet: ClaimPacket, 
                                validation: ClaimValidation) -> ProofCard:
        """Generate cryptographic proof card for a validated claim"""
        
        # Serialize claim packet for hashing
        claim_data = {
            "claim_id": claim_packet.claim_id,
            "policy_number": claim_packet.policy_number,
            "claimant_name": claim_packet.claimant_name,
            "incident_date": claim_packet.incident_date.isoformat(),
            "property_address": claim_packet.property_address,
            "documents": [
                {
                    "id": doc.id,
                    "filename": doc.filename,
                    "document_type": doc.document_type,
                    "extracted_data": doc.extracted_data
                }
                for doc in claim_packet.documents
            ],
            "validation": {
                "overall_score": validation.overall_score,
                "approved": validation.approved,
                "rules_evaluated": [
                    {
                        "rule_id": rule.rule_id,
                        "passed": rule.passed,
                        "confidence": rule.confidence
                    }
                    for rule in validation.rules_evaluated
                ]
            }
        }
        
        # Create deterministic hash of claim data
        claim_json = json.dumps(claim_data, sort_keys=True)
        claim_hash = hashlib.sha256(claim_json.encode()).hexdigest()
        
        # Sign the claim hash with AI agent's private key
        message_hash = self.w3.keccak(text=claim_hash)
        signature = self.account.sign_message_hash(message_hash)
        
        # Create proof card
        proof_card = ProofCard(
            claim_hash=claim_hash,
            agent_signature=signature.signature.hex(),
            timestamp=int(time.time()),
            judge_score=validation.overall_score,
            validation_rules_version="v1.0"
        )
        
        return proof_card
    
    async def anchor_to_sepolia(self, proof_card: ProofCard) -> Optional[str]:
        """Anchor proof card to Sepolia blockchain"""
        
        if not self.contract or not self.w3.is_connected():
            print("Blockchain not available, storing proof locally")
            return self._store_proof_locally(proof_card)
        
        try:
            # Convert claim hash to bytes32
            claim_hash_bytes = self.w3.keccak(text=proof_card.claim_hash)
            
            # Prepare transaction
            function_call = self.contract.functions.registerClaim(
                claim_hash_bytes,
                bytes.fromhex(proof_card.agent_signature.replace('0x', '')),
                int(proof_card.judge_score * 1000),  # Convert to integer (3 decimal places)
                proof_card.timestamp
            )
            
            # Build transaction
            transaction = function_call.build_transaction({
                'from': self.account.address,
                'nonce': self.w3.eth.get_transaction_count(self.account.address),
                'gas': 200000,
                'gasPrice': self.w3.to_wei('20', 'gwei')
            })
            
            # Sign and send transaction
            signed_txn = self.account.sign_transaction(transaction)
            tx_hash = self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)
            
            # Wait for confirmation
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
            
            if receipt.status == 1:
                tx_hash_hex = tx_hash.hex()
                proof_card.blockchain_tx_hash = tx_hash_hex
                print(f"Claim anchored to blockchain: {tx_hash_hex}")
                return tx_hash_hex
            else:
                print("Transaction failed")
                return None
                
        except Exception as e:
            print(f"Error anchoring to blockchain: {e}")
            return self._store_proof_locally(proof_card)
    
    async def verify_claim(self, claim_hash: str) -> Dict[str, Any]:
        """Verify a claim on the blockchain"""
        
        if not self.contract:
            return {"verified": False, "error": "Blockchain not available"}
        
        try:
            # Convert claim hash to bytes32
            claim_hash_bytes = self.w3.keccak(text=claim_hash)
            
            # Query blockchain
            result = self.contract.functions.claims(claim_hash_bytes).call()
            
            if result[0] == b'\x00' * 32:  # Empty hash means not found
                return {"verified": False, "error": "Claim not found on blockchain"}
            
            return {
                "verified": True,
                "claim_hash": result[0].hex(),
                "signature": result[1].hex(),
                "timestamp": result[2],
                "score": result[3] / 1000.0,  # Convert back from integer
                "is_valid": result[4] if len(result) > 4 else True
            }
            
        except Exception as e:
            print(f"Error verifying claim: {e}")
            return {"verified": False, "error": str(e)}
    
    def _store_proof_locally(self, proof_card: ProofCard) -> str:
        """Store proof card locally when blockchain is not available"""
        
        # Create local storage directory
        os.makedirs("local_proofs", exist_ok=True)
        
        # Generate local transaction hash
        local_tx_hash = f"local_{proof_card.claim_hash[:16]}"
        
        # Store proof card
        proof_file = f"local_proofs/{local_tx_hash}.json"
        with open(proof_file, 'w') as f:
            json.dump({
                "claim_hash": proof_card.claim_hash,
                "agent_signature": proof_card.agent_signature,
                "timestamp": proof_card.timestamp,
                "judge_score": proof_card.judge_score,
                "validation_rules_version": proof_card.validation_rules_version,
                "local_storage": True
            }, f, indent=2)
        
        print(f"Proof stored locally: {proof_file}")
        return local_tx_hash
    
    def generate_verification_url(self, tx_hash: str) -> str:
        """Generate verification URL for the transaction"""
        
        # Get base URL from environment or use production URL
        base_url = os.getenv("API_BASE_URL", "https://kava-backend.onrender.com")
        
        if tx_hash.startswith("local_"):
            return f"{base_url}/api/verify-local/{tx_hash}"
        else:
            return f"https://sepolia.etherscan.io/tx/{tx_hash}"
    
    def get_account_info(self) -> Dict[str, str]:
        """Get account information for the AI agent"""
        return {
            "address": self.account.address,
            "balance": str(self.w3.eth.get_balance(self.account.address)) if self.w3.is_connected() else "0",
            "network": "Sepolia Testnet" if self.w3.is_connected() else "Disconnected"
        }
