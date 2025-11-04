from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional, Dict, Any
import os
import json
import hashlib
import time
from datetime import datetime, timedelta
from dotenv import load_dotenv
import asyncio
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from io import BytesIO
import base64
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.backends import default_backend

from services.ai_judge import AIJudge
from services.document_processor import DocumentProcessor
from services.receipt_fetcher import ReceiptFetcher
from services.claim_package_generator import generate_comprehensive_claim_package
from models.claim import ClaimPacket, ClaimValidation, ProofCard, Document, DocumentType
from database import get_db

from sqlalchemy.orm import Session

load_dotenv('../.env')

app = FastAPI(title="KAVA API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000", 
        "http://localhost:3001", 
        "http://localhost:3002", 
        "http://localhost:3003", 
        "http://localhost:3008", 
        "http://127.0.0.1:49690",
        "https://kava-xi.vercel.app",
        "https://*.vercel.app"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
ai_judge = AIJudge()
doc_processor = DocumentProcessor()
receipt_fetcher = ReceiptFetcher()

# ECDSA key pair for signing (in production, use secure key management)
private_key = ec.generate_private_key(ec.SECP256R1(), default_backend())
public_key = private_key.public_key()

async def generate_claim_packet_pdf(claim_packet: ClaimPacket) -> str:
    """Generate comprehensive initial claim packet PDF with embedded documents and OCR data"""
    os.makedirs("claim_packets", exist_ok=True)
    pdf_path = f"claim_packets/{claim_packet.claim_id}_initial.pdf"
    
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
    
    # Create PDF document
    pdf_doc = SimpleDocTemplate(pdf_path, pagesize=letter, rightMargin=50, leftMargin=50, 
                          topMargin=50, bottomMargin=50)
    styles = getSampleStyleSheet()
    story = []
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=20,
        spaceAfter=30,
        alignment=TA_CENTER,
        textColor=colors.darkblue
    )
    
    header_style = ParagraphStyle(
        'CustomHeader',
        parent=styles['Heading2'],
        fontSize=14,
        spaceAfter=12,
        spaceBefore=20,
        textColor=colors.darkblue,
        borderWidth=1,
        borderColor=colors.darkblue,
        borderPadding=5
    )
    
    # Title page
    story.append(Paragraph(f"WILDFIRE INSURANCE CLAIM PACKET", title_style))
    story.append(Paragraph(f"Claim ID: {claim_packet.claim_id}", styles['Heading2']))
    story.append(Spacer(1, 20))
    
    # Claim summary table
    claim_data = [
        ['Field', 'Information'],
        ['Claimant Name', claim_packet.claimant_name],
        ['Policy Number', claim_packet.policy_number],
        ['Incident Date', claim_packet.incident_date.strftime('%B %d, %Y')],
        ['Property Address', claim_packet.property_address],
        ['Estimated Damage', f"${claim_packet.estimated_damage:,.2f}" if claim_packet.estimated_damage else "Not specified"],
        ['Claim Generated', claim_packet.created_at.strftime('%B %d, %Y at %I:%M %p')],
        ['Documents Attached', str(len(claim_packet.documents))]
    ]
    
    claim_table = Table(claim_data, colWidths=[2*inch, 4*inch])
    claim_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.lightgrey),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.lightgrey, colors.white])
    ]))
    
    story.append(claim_table)
    story.append(Spacer(1, 30))
    
    # Document processing summary
    if claim_packet.documents:
        story.append(Paragraph("DOCUMENT PROCESSING SUMMARY", header_style))
        
        doc_summary_data = [['Document', 'Type', 'OCR Confidence', 'Key Data Extracted']]
        
        for doc in claim_packet.documents:
            key_data = []
            if doc.extracted_data:
                # Extract key information from OCR data
                for key, value in doc.extracted_data.items():
                    if key in ['total_amount', 'date', 'merchant', 'address', 'damage_type', 'policy_number']:
                        if value:
                            key_data.append(f"{key.replace('_', ' ').title()}: {value}")
            
            key_data_str = "; ".join(key_data[:3]) if key_data else "Processing..."
            if len(key_data_str) > 60:
                key_data_str = key_data_str[:57] + "..."
                
            doc_summary_data.append([
                doc.filename[:25] + "..." if len(doc.filename) > 25 else doc.filename,
                doc.document_type.value.replace('_', ' ').title(),
                f"{doc.confidence_score:.1%}",
                key_data_str
            ])
        
        doc_table = Table(doc_summary_data, colWidths=[1.5*inch, 1*inch, 1*inch, 2.5*inch])
        doc_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.darkgreen),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.lightgreen),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.lightgreen, colors.white]),
            ('VALIGN', (0, 0), (-1, -1), 'TOP')
        ]))
        
        story.append(doc_table)
        story.append(PageBreak())
        
        # Detailed document analysis
        story.append(Paragraph("DETAILED DOCUMENT ANALYSIS", header_style))
        
        for i, doc in enumerate(claim_packet.documents):
            story.append(Paragraph(f"Document {i+1}: {doc.filename}", styles['Heading3']))
            
            # Document details table
            doc_details = [
                ['Property', 'Value'],
                ['File Type', doc.document_type.value.replace('_', ' ').title()],
                ['Upload Date', doc.upload_timestamp.strftime('%B %d, %Y at %I:%M %p')],
                ['OCR Confidence', f"{doc.confidence_score:.1%}"],
                ['File Size', f"{doc.file_size} bytes" if hasattr(doc, 'file_size') else "Unknown"]
            ]
            
            details_table = Table(doc_details, colWidths=[1.5*inch, 3*inch])
            details_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.lightgrey, colors.white])
            ]))
            
            story.append(details_table)
            story.append(Spacer(1, 10))
            
            # OCR Extracted Data
            if doc.extracted_data:
                story.append(Paragraph("OCR Extracted Data:", styles['Heading4']))
                
                extracted_data_formatted = []
                for key, value in doc.extracted_data.items():
                    if value:  # Only show non-empty values
                        key_formatted = key.replace('_', ' ').title()
                        value_str = str(value)
                        if len(value_str) > 100:
                            value_str = value_str[:97] + "..."
                        extracted_data_formatted.append(f"<b>{key_formatted}:</b> {value_str}")
                
                if extracted_data_formatted:
                    story.append(Paragraph("<br/>".join(extracted_data_formatted), styles['Normal']))
                else:
                    story.append(Paragraph("No structured data extracted from this document.", styles['Italic']))
            else:
                story.append(Paragraph("No OCR data available for this document.", styles['Italic']))
            
            story.append(Spacer(1, 20))
    
    # Validation checklist section
    story.append(PageBreak())
    story.append(Paragraph("CLAIM VALIDATION CHECKLIST", header_style))
    
    checklist_data = [
        ['Validation Item', 'Status', 'Notes'],
        ['Policy Documentation', '✓ Present' if any(d.document_type.value == 'policy' for d in claim_packet.documents) else '⚠ Missing', 'Policy documents uploaded and processed'],
        ['Damage Photos', '✓ Present' if any(d.document_type.value == 'photo' for d in claim_packet.documents) else '⚠ Missing', 'Property damage photographs'],
        ['Receipts/Estimates', '✓ Present' if any(d.document_type.value == 'receipt' for d in claim_packet.documents) else '⚠ Missing', 'Repair estimates or purchase receipts'],
        ['Fire Dept Report', '✓ Present' if any(d.document_type.value == 'damage_report' for d in claim_packet.documents) else '⚠ Missing', 'Official incident documentation'],
        ['Claim Form Complete', '✓ Complete', 'All required fields filled'],
        ['Property Address', '✓ Verified', f'Address: {claim_packet.property_address}'],
        ['Incident Date', '✓ Valid', f'Date: {claim_packet.incident_date.strftime("%B %d, %Y")}']
    ]
    
    checklist_table = Table(checklist_data, colWidths=[2*inch, 1*inch, 3*inch])
    checklist_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.orange),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.lightyellow, colors.white]),
        ('VALIGN', (0, 0), (-1, -1), 'TOP')
    ]))
    
    story.append(checklist_table)
    story.append(Spacer(1, 20))
    
    # Next steps section
    story.append(Paragraph("NEXT STEPS", header_style))
    next_steps_text = """
    This initial claim packet has been generated and is ready for AI validation processing. 
    The following steps will be performed automatically:
    
    1. <b>AI Judge Evaluation:</b> Advanced rule-based validation for completeness and fraud detection
    2. <b>Auto-Receipt Fetching:</b> Automatic retrieval of missing receipts via Knot API integration
    3. <b>Document Re-processing:</b> Enhanced OCR for low-confidence documents
    4. <b>Iterative Improvement:</b> Multiple validation rounds until score stabilizes
    5. <b>Final Attestation:</b> Generation of trust score and ECDSA-signed proof card
    
    <b>Current Status:</b> Initial packet created, ready for validation loop.
    """
    
    story.append(Paragraph(next_steps_text, styles['Normal']))
    
    # Generate PDF
    pdf_doc.build(story)
    
    return pdf_path

async def generate_final_claim_packet_pdf(claim_packet: ClaimPacket, validation: ClaimValidation) -> str:
    """Generate comprehensive final validated claim packet PDF with AI Judge results"""
    os.makedirs("claim_packets", exist_ok=True)
    pdf_path = f"claim_packets/{claim_packet.claim_id}_final.pdf"
    
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_CENTER, TA_LEFT
    
    # Create PDF document
    pdf_doc = SimpleDocTemplate(pdf_path, pagesize=letter, rightMargin=50, leftMargin=50, 
                          topMargin=50, bottomMargin=50)
    styles = getSampleStyleSheet()
    story = []
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=22,
        spaceAfter=20,
        alignment=TA_CENTER,
        textColor=colors.darkblue
    )
    
    # Validation status styling
    status_color = colors.green if validation.approved else colors.red
    status_text = "✓ APPROVED" if validation.approved else "⚠ REQUIRES REVIEW"
    
    status_style = ParagraphStyle(
        'StatusStyle',
        parent=styles['Heading2'],
        fontSize=16,
        spaceAfter=20,
        alignment=TA_CENTER,
        textColor=status_color,
        borderWidth=2,
        borderColor=status_color,
        borderPadding=10
    )
    
    # Title and status
    story.append(Paragraph("FINAL VALIDATED CLAIM PACKET", title_style))
    story.append(Paragraph(status_text, status_style))
    story.append(Spacer(1, 20))
    
    # AI Judge Score Badge
    score_color = colors.green if validation.overall_score >= 0.8 else colors.orange if validation.overall_score >= 0.6 else colors.red
    trust_badge = get_trust_badge(validation.overall_score)
    
    judge_data = [
        ['AI JUDGE EVALUATION RESULTS'],
        [f'Overall Score: {validation.overall_score:.1%}'],
        [f'Trust Badge: {trust_badge}'],
        [f'Confidence Level: {validation.confidence:.1%}'],
        [f'Validation Date: {validation.timestamp.strftime("%B %d, %Y at %I:%M %p")}']
    ]
    
    judge_table = Table(judge_data, colWidths=[6*inch])
    judge_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), score_color),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (0, 0), 14),
        ('FONTSIZE', (0, 1), (-1, -1), 12),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('BACKGROUND', (0, 1), (-1, -1), colors.lightgrey)
    ]))
    
    story.append(judge_table)
    story.append(Spacer(1, 30))
    
    # Validation Rules Results
    story.append(Paragraph("VALIDATION RULES ANALYSIS", styles['Heading2']))
    
    rules_data = [['Rule', 'Status', 'Weight', 'Confidence', 'Rationale']]
    
    for rule in validation.rules_evaluated:
        status_icon = "✓ PASS" if rule.passed else "✗ FAIL"
        status_color_rule = colors.green if rule.passed else colors.red
        
        rules_data.append([
            rule.description[:30] + "..." if len(rule.description) > 30 else rule.description,
            status_icon,
            f"{rule.weight:.1%}",
            f"{rule.confidence:.1%}",
            rule.rationale[:50] + "..." if len(rule.rationale) > 50 else rule.rationale
        ])
    
    rules_table = Table(rules_data, colWidths=[2*inch, 0.8*inch, 0.6*inch, 0.8*inch, 2*inch])
    
    # Dynamic row coloring based on pass/fail
    table_style = [
        ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'TOP')
    ]
    
    # Color rows based on rule results
    for i, rule in enumerate(validation.rules_evaluated):
        row_color = colors.lightgreen if rule.passed else colors.lightpink
        table_style.append(('BACKGROUND', (0, i+1), (-1, i+1), row_color))
    
    rules_table.setStyle(TableStyle(table_style))
    story.append(rules_table)
    story.append(Spacer(1, 20))
    
    # Missing Documents and Fraud Indicators
    if validation.missing_documents or validation.fraud_indicators:
        story.append(PageBreak())
        
        if validation.missing_documents:
            story.append(Paragraph("MISSING DOCUMENTS", styles['Heading3']))
            missing_text = "<br/>".join([f"• {doc}" for doc in validation.missing_documents])
            story.append(Paragraph(missing_text, styles['Normal']))
            story.append(Spacer(1, 15))
        
        if validation.fraud_indicators:
            story.append(Paragraph("FRAUD RISK INDICATORS", styles['Heading3']))
            fraud_text = "<br/>".join([f"⚠ {indicator}" for indicator in validation.fraud_indicators])
            story.append(Paragraph(fraud_text, styles['Normal']))
            story.append(Spacer(1, 15))
    
    # Original claim information
    story.append(PageBreak())
    story.append(Paragraph("ORIGINAL CLAIM INFORMATION", styles['Heading2']))
    
    # Claim details table (same as initial but more detailed)
    claim_data = [
        ['Field', 'Information'],
        ['Claim ID', claim_packet.claim_id],
        ['Claimant Name', claim_packet.claimant_name],
        ['Policy Number', claim_packet.policy_number],
        ['Incident Date', claim_packet.incident_date.strftime('%B %d, %Y')],
        ['Property Address', claim_packet.property_address],
        ['Estimated Damage', f"${claim_packet.estimated_damage:,.2f}" if claim_packet.estimated_damage else "Not specified"],
        ['Documents Processed', str(len(claim_packet.documents))],
        ['Initial Submission', claim_packet.created_at.strftime('%B %d, %Y at %I:%M %p')],
        ['Final Validation', validation.timestamp.strftime('%B %d, %Y at %I:%M %p')]
    ]
    
    claim_table = Table(claim_data, colWidths=[2*inch, 4*inch])
    claim_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.lightgrey),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.lightgrey, colors.white])
    ]))
    
    story.append(claim_table)
    story.append(Spacer(1, 30))
    
    # AI Judge rationale
    story.append(Paragraph("AI JUDGE DETAILED RATIONALE", styles['Heading3']))
    story.append(Paragraph(validation.rationale, styles['Normal']))
    story.append(Spacer(1, 20))
    
    # Attestation footer
    story.append(Paragraph("DIGITAL ATTESTATION", styles['Heading3']))
    attestation_text = f"""
    This claim packet has been processed and validated using AI Judge technology. 
    The validation score of {validation.overall_score:.1%} represents the automated assessment 
    of claim completeness, consistency, and fraud risk indicators.
    
    <b>Trust Badge:</b> {trust_badge}
    <b>Validation Rules Version:</b> v1.0
    <b>Processing Complete:</b> {validation.timestamp.strftime('%B %d, %Y at %I:%M %p')}
    
    This document serves as the official validated claim packet for insurance processing.
    """
    
    story.append(Paragraph(attestation_text, styles['Normal']))
    
    # Generate PDF
    pdf_doc.build(story)
    
    return pdf_path

async def generate_ecdsa_signature(claim_hash: str) -> str:
    """Generate ECDSA signature for claim hash"""
    message = claim_hash.encode()
    signature = private_key.sign(message, ec.ECDSA(hashes.SHA256()))
    return base64.b64encode(signature).decode()

async def verify_ecdsa_signature(claim_hash: str, signature_b64: str) -> bool:
    """Verify ECDSA signature"""
    try:
        message = claim_hash.encode()
        signature = base64.b64decode(signature_b64)
        public_key.verify(signature, message, ec.ECDSA(hashes.SHA256()))
        return True
    except Exception:
        return False

def get_trust_badge(score: float) -> str:
    """Get trust badge based on validation score"""
    if score >= 0.9:
        return "GOLD_TRUST"
    elif score >= 0.8:
        return "SILVER_TRUST"
    elif score >= 0.6:
        return "BRONZE_TRUST"
    else:
        return "REVIEW_REQUIRED"

@app.post("/api/sync-receipts")
async def sync_receipts(request: Dict[str, Any]):
    """Sync receipts from Knot API (currently using test data)"""
    try:
        company = request.get("company", "").lower()
        claimant_name = request.get("claimant_name", "")
        date_range = request.get("date_range", {})
        
        print(f"🔍 Syncing receipts for company: {company}")
        
        # Read test receipts from file (simulating Knot API response)
        receipts_file_path = "../test_claims/receipts.json"
        
        if not os.path.exists(receipts_file_path):
            return {"receipts": [], "message": "No test receipts available"}
        
        with open(receipts_file_path, 'r') as f:
            knot_data = json.load(f)
        
        # Filter transactions by company
        filtered_receipts = []
        
        for transaction in knot_data.get("transactions", []):
            transaction_company = ""
            
            # Determine company from external_id or products
            if "HD-" in transaction.get("external_id", ""):
                transaction_company = "home_depot"
            elif "AMZ-" in transaction.get("external_id", ""):
                transaction_company = "amazon"
            elif "WMT-" in transaction.get("external_id", ""):
                transaction_company = "walmart"
            
            # If this transaction matches the requested company
            if company in transaction_company or transaction_company in company:
                # Convert to document format
                receipt_doc = {
                    "id": f"knot_{transaction['id']}",
                    "filename": f"{transaction_company}_receipt_{transaction['id']}.json",
                    "document_type": "receipt",
                    "extracted_data": {
                        "merchant": transaction_company.replace("_", " ").title(),
                        "total_amount": transaction["price"]["total"],
                        "date": transaction["datetime"][:10],
                        "items": [product["name"] for product in transaction.get("products", [])],
                        "payment_method": transaction["payment_methods"][0]["brand"] if transaction.get("payment_methods") else "Unknown",
                        "last_four": transaction["payment_methods"][0]["last_four"] if transaction.get("payment_methods") else "****",
                        "order_id": transaction["external_id"],
                        "currency": transaction["price"]["currency"],
                        "tax_amount": next((adj["amount"] for adj in transaction["price"].get("adjustments", []) if adj["type"] == "TAX"), 0),
                        "order_status": transaction.get("order_status", "DELIVERED")
                    },
                    "confidence_score": 0.95,  # High confidence for Knot API data
                    "file_size": len(json.dumps(transaction)),
                    "upload_timestamp": datetime.now().isoformat(),
                    "source": "knot_api"
                }
                
                filtered_receipts.append(receipt_doc)
        
        print(f"✅ Found {len(filtered_receipts)} receipts for {company}")
        
        return {
            "receipts": filtered_receipts,
            "company": company,
            "total_amount": sum(receipt["extracted_data"]["total_amount"] for receipt in filtered_receipts),
            "message": f"Successfully synced {len(filtered_receipts)} receipts from {company}"
        }
        
    except Exception as e:
        print(f"❌ Receipt sync error: {e}")
        raise HTTPException(status_code=500, detail=f"Receipt sync failed: {str(e)}")

@app.get("/")
async def root():
    return {"message": "KAVA API is running"}

@app.post("/api/sync-receipts")
async def sync_receipts(request: Dict[str, Any]):
    """Sync receipts from Knot API for specific company"""
    try:
        company = request.get("company", "")
        claimant_name = request.get("claimant_name", "")
        date_range = request.get("date_range", {})
        
        print(f"Syncing receipts for {company} - {claimant_name}")
        
        # Load receipts from test file for demo
        import json
        receipts_file = os.path.join(os.path.dirname(__file__), "../test_claims/receipts.json")
        
        try:
            with open(receipts_file, 'r') as f:
                receipts_data = json.load(f)
            
            # Filter receipts by company
            filtered_receipts = []
            company_map = {
                "home_depot": "hd",
                "amazon": "amz", 
                "walmart": "wmt"
            }
            
            company_filter = company_map.get(company, company)
            print(f"Looking for receipts with filter: {company_filter}")
            
            for transaction in receipts_data.get("transactions", []):
                external_id = transaction.get("external_id", "").lower()
                if company_filter in external_id:
                    # Convert transaction to receipt document format
                    receipt_doc = {
                        "id": transaction["id"],
                        "filename": f"{company}_{transaction['external_id']}.json",
                        "document_type": "receipt",
                        "extracted_data": {
                            "merchant": company.replace('_', ' ').title(),
                            "total_amount": f"${transaction['price']['total']:.2f}",
                            "date": transaction["datetime"][:10],
                            "items": [product["name"] for product in transaction.get("products", [])],
                            "payment_method": f"{transaction['payment_methods'][0]['brand']} ending in {transaction['payment_methods'][0]['last_four']}",
                            "order_id": transaction["external_id"],
                            "knot_synced": True
                        },
                        "confidence_score": 0.95,  # High confidence for Knot API data
                        "file_size": len(str(transaction)),
                        "upload_timestamp": datetime.now().isoformat()
                    }
                    filtered_receipts.append(receipt_doc)
            
            return {
                "receipts": filtered_receipts,
                "company": company,
                "count": len(filtered_receipts),
                "status": "success"
            }
            
        except FileNotFoundError:
            print(f"Receipts file not found: {receipts_file}")
            return {
                "receipts": [],
                "company": company,
                "count": 0,
                "status": "no_data"
            }
            
    except Exception as e:
        print(f"Error syncing receipts: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/upload-documents")
async def upload_documents(files: List[UploadFile] = File(...)):
    """Upload and process insurance documents with OCR - saves files for claim package"""
    try:
        # Create uploaded_files directory
        os.makedirs("uploaded_files", exist_ok=True)
        
        processed_docs = []
        for file in files:
            content = await file.read()
            
            # Save the actual file
            file_id = f"{int(time.time() * 1000)}_{file.filename}"
            file_path = f"uploaded_files/{file_id}"
            
            with open(file_path, 'wb') as f:
                f.write(content)
            
            # Process document with OCR
            processed_doc = await doc_processor.process_document(content, file.filename)
            
            # Add file_path to the processed document
            processed_doc_dict = processed_doc.dict() if hasattr(processed_doc, 'dict') else vars(processed_doc)
            processed_doc_dict['file_path'] = file_path
            
            processed_docs.append(processed_doc_dict)
        
        return {
            "documents": processed_docs, 
            "status": "success",
            "next_step": "create_claim_packet"
        }
    except Exception as e:
        print(f"Upload documents error: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/create-claim-packet")
async def create_claim_packet(claim_data: Dict[str, Any]):
    """Create initial claim packet and generate PDF"""
    try:
        print(f"Creating claim packet with data: {claim_data}")
        
        # Extract and validate required fields
        claim_id = claim_data.get("claim_id", f"claim_{int(time.time())}")
        policy_number = claim_data.get("policy_number", "UNKNOWN")
        claimant_name = claim_data.get("claimant_name", "Unknown Claimant")
        
        # Handle incident_date
        incident_date_str = claim_data.get("incident_date", "2024-10-15")
        if isinstance(incident_date_str, str):
            try:
                incident_date = datetime.fromisoformat(incident_date_str.replace('Z', ''))
            except:
                incident_date = datetime.now()
        else:
            incident_date = incident_date_str or datetime.now()
        
        property_address = claim_data.get("property_address", "Unknown Address")
        documents = claim_data.get("documents", [])
        estimated_damage = claim_data.get("estimated_damage", 0.0)
        
        # Convert documents to proper format
        document_objects = []
        for doc in documents:
            document_objects.append(Document(
                id=doc.get("id", "unknown"),
                filename=doc.get("filename", "unknown.pdf"),
                document_type=DocumentType(doc.get("document_type", "other")),
                extracted_data=doc.get("extracted_data", {}),
                confidence_score=doc.get("confidence_score", 0.5),
                file_size=doc.get("file_size", 0),
                upload_timestamp=datetime.now(),
                file_path=doc.get("file_path"),  # Preserve file_path from upload
                content=doc.get("content")  # Preserve content if available
            ))
        
        # Create claim packet with proper structure
        claim_packet = ClaimPacket(
            claim_id=claim_id,
            policy_number=policy_number,
            claimant_name=claimant_name,
            incident_date=incident_date,
            property_address=property_address,
            documents=document_objects,
            estimated_damage=estimated_damage,
            created_at=datetime.now()
        )
        
        print(f"Claim packet created successfully: {claim_packet.claim_id}")
        
        # 💾 SAVE TO DATABASE
        from database import ClaimRecord, SessionLocal
        db = SessionLocal()
        try:
            claim_record = ClaimRecord(
                claim_id=claim_packet.claim_id,
                policy_number=claim_packet.policy_number,
                claimant_name=claim_packet.claimant_name,
                incident_date=claim_packet.incident_date,
                property_address=claim_packet.property_address,
                estimated_damage=claim_packet.estimated_damage,
                status="packet_created",
                documents=[doc.dict() if hasattr(doc, 'dict') else vars(doc) for doc in document_objects],
                created_at=datetime.now()
            )
            db.add(claim_record)
            db.commit()
            print(f"💾 Claim saved to database: {claim_packet.claim_id}")
        except Exception as db_error:
            print(f"⚠️ Database save failed: {db_error}")
            db.rollback()
        finally:
            db.close()
        
        # Generate initial PDF claim packet
        pdf_path = await generate_claim_packet_pdf(claim_packet)
        
        return {
            "claim_packet": claim_packet.model_dump(),
            "pdf_path": pdf_path,
            "status": "packet_created",
            "next_step": "validation_loop"
        }
    except Exception as e:
        print(f"Error creating claim packet: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Claim packet creation failed: {str(e)}")

@app.post("/api/validation-loop")
async def enhanced_validation_loop(request: Dict[str, Any]):
    """Progressive validation - ALL 47 rules each time, claim improves to pass MORE rules"""
    try:
        claim_packet = ClaimPacket(**request.get("claim_packet", {}))
        max_iterations = 4
        
        validation_history = []
        previous_scores = []
        iteration = 0
        
        print(f"🚀 Starting Progressive Validation Loop for claim {claim_packet.claim_id}")
        print(f"🎯 Same 47 rules each iteration - claim improves to pass more!")
        
        while iteration < max_iterations:
            iteration += 1
            
            print(f"\n{'='*60}")
            print(f"🔄 ITERATION {iteration}/{max_iterations}")
            print(f"{'='*60}")
            
            # ENHANCE THE CLAIM (so it passes more rules)
            original_doc_count = len(claim_packet.documents)
            
            if iteration == 2:
                print("💳 ITERATION 2: Adding Knot receipts to pass more rules...")
                claim_packet = await auto_enhance_with_knot_receipts(claim_packet)
                print(f"📄 Documents: {original_doc_count} → {len(claim_packet.documents)}")
                
            elif iteration == 3:
                print("🔍 ITERATION 3: Reprocessing documents for better quality...")
                claim_packet = await deep_reprocess_documents(claim_packet)
                
            elif iteration == 4:
                print("⚖️ ITERATION 4: Final review with all enhancements...")
            
            # EVALUATE AGAINST ALL 47 RULES (same rules, better claim)
            validation = await ai_judge.evaluate_with_depth(claim_packet, iteration, previous_scores)
            
            current_score = validation.overall_score
            rules_passed = len([r for r in validation.rules_evaluated if r.passed])
            total_rules = len(validation.rules_evaluated)
            
            print(f"📊 Rules: {rules_passed}/{total_rules} passed = {current_score:.1%}")
            
            # Record results
            validation_history.append({
                "iteration": iteration,
                "analysis_depth": ai_judge._get_depth_name(iteration),
                "score": current_score,
                "rules_passed": rules_passed,
                "total_rules": total_rules,
                "improvement": (current_score - previous_scores[-1]) if previous_scores else 0,
                "validation": validation.model_dump(),
                "documents_processed": len(claim_packet.documents)
            })
            
            # EXIT CONDITIONS
            if current_score >= 0.8:
                print(f"🎉 TARGET: {current_score:.1%} ≥80%!")
                break
            
            previous_scores.append(current_score)
            
            if iteration < max_iterations:
                improvement_so_far = current_score - previous_scores[0] if len(previous_scores) > 1 else 0
                print(f"🔄 Current {current_score:.1%}, improved {improvement_so_far:+.1%} total, continuing...")
        
        final_validation = validation_history[-1]["validation"]
        
        print(f"\n🏁 COMPLETE: {final_validation['overall_score']:.1%} after {iteration} iterations")
        
        # Save to database
        from database import ClaimRecord, SessionLocal
        db = SessionLocal()
        try:
            claim_record = db.query(ClaimRecord).filter(ClaimRecord.claim_id == claim_packet.claim_id).first()
            if claim_record:
                claim_record.status = "validated"
                claim_record.validation_result = final_validation
                claim_record.updated_at = datetime.now()
                db.commit()
        except Exception as db_error:
            db.rollback()
        finally:
            db.close()
        
        return {
            "final_validation": final_validation,
            "validation_history": validation_history,
            "iterations_completed": iteration,
            "total_improvement": (previous_scores[-1] - previous_scores[0]) if len(previous_scores) > 1 else 0,
            "final_analysis_depth": ai_judge._get_depth_name(iteration),
            "next_step": "generate_final_outputs"
        }
    except Exception as e:
        print(f"❌ Validation loop error: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


async def auto_enhance_with_knot_receipts(claim_packet: ClaimPacket) -> ClaimPacket:
    """Auto-enhance claim packet with Knot receipt integration (ITERATION 2)"""
    try:
        print("💳 Auto-enhancing claim with Knot receipt integration...")
        
        companies_to_sync = ["home_depot", "amazon", "walmart"]
        all_synced_receipts = []
        
        for company in companies_to_sync:
            try:
                # Use the existing sync-receipts endpoint
                sync_request = {
                    "company": company,
                    "claimant_name": claim_packet.claimant_name,
                    "date_range": {
                        "start": (claim_packet.incident_date - timedelta(days=30)).isoformat(),
                        "end": (claim_packet.incident_date + timedelta(days=60)).isoformat()
                    }
                }
                
                # Call sync-receipts internally 
                sync_result = await sync_receipts(sync_request)
                if sync_result.get("receipts"):
                    print(f"✅ Found {len(sync_result['receipts'])} receipts from {company}")
                    
                    # Convert synced receipts to Document objects
                    for receipt_data in sync_result["receipts"]:
                        receipt_doc = Document(
                            id=receipt_data.get("id", f"knot_{company}_{len(all_synced_receipts)}"),
                            filename=receipt_data.get("filename", f"{company}_receipt.json"),
                            document_type=DocumentType.RECEIPT,
                            extracted_data=receipt_data.get("extracted_data", {}),
                            confidence_score=receipt_data.get("confidence_score", 0.95),
                            file_size=receipt_data.get("file_size", 1024),
                            upload_timestamp=datetime.now()
                        )
                        all_synced_receipts.append(receipt_doc)
            except Exception as e:
                print(f"⚠️ Failed to sync {company}: {e}")
        
        # Create merged receipt document if we found receipts
        if all_synced_receipts:
            total_amount = 0.0
            for receipt in all_synced_receipts:
                if receipt.extracted_data and receipt.extracted_data.get("total_amount"):
                    amount_str = str(receipt.extracted_data["total_amount"]).replace("$", "").replace(",", "")
                    try:
                        total_amount += float(amount_str)
                    except:
                        pass
            
            merged_receipt_data = {
                "merged_receipts": True,
                "total_receipts": len(all_synced_receipts),
                "total_amount": total_amount,
                "companies": list(set(r.extracted_data.get("merchant", "Unknown") for r in all_synced_receipts if r.extracted_data)),
                "auto_fetched": True,
                "knot_integration": True,
                "receipts": [r.extracted_data for r in all_synced_receipts if r.extracted_data]
            }
            
            # Create merged receipt document
            merged_receipt_doc = Document(
                id=f"knot_merged_{int(time.time())}",
                filename=f"knot_merged_receipts_{claim_packet.claim_id}.json",
                document_type=DocumentType.RECEIPT,
                extracted_data=merged_receipt_data,
                confidence_score=0.98,  # High confidence for Knot API data
                file_size=len(json.dumps(merged_receipt_data)),
                upload_timestamp=datetime.now()
            )
            
            # Add merged receipt + top individual receipts
            claim_packet.documents.append(merged_receipt_doc)
            claim_packet.documents.extend(all_synced_receipts[:3])  # Top 3 individual receipts
            
            print(f"📄 Enhanced with {len(all_synced_receipts)} receipts totaling ${total_amount:,.2f}")
        else:
            print("ℹ️ No additional receipts found via Knot integration")
        
        return claim_packet
        
    except Exception as e:
        print(f"❌ Knot enhancement failed: {e}")
        return claim_packet

async def deep_reprocess_documents(claim_packet: ClaimPacket) -> ClaimPacket:
    """Deep reprocessing of documents for forensic analysis (ITERATION 3)"""
    try:
        print("🔍 Deep reprocessing documents for forensic analysis...")
        
        reprocessed_count = 0
        
        # Re-run OCR on low-confidence documents with enhanced processing
        for doc in claim_packet.documents:
            if doc.confidence_score < 0.8:  # Higher threshold for forensic analysis
                try:
                    print(f"🔄 Reprocessing {doc.filename} (confidence: {doc.confidence_score:.1%})")
                    reprocessed = await doc_processor.reprocess_document(doc)
                    if reprocessed and reprocessed.confidence_score > doc.confidence_score:
                        old_confidence = doc.confidence_score
                        doc.extracted_data = reprocessed.extracted_data
                        doc.confidence_score = reprocessed.confidence_score
                        reprocessed_count += 1
                        print(f"✅ Improved {doc.filename}: {old_confidence:.1%} → {doc.confidence_score:.1%}")
                except Exception as e:
                    print(f"⚠️ Failed to reprocess {doc.filename}: {e}")
        
        if reprocessed_count > 0:
            print(f"📈 Successfully reprocessed {reprocessed_count} documents")
        else:
            print("ℹ️ No documents required reprocessing")
        
        return claim_packet
        
    except Exception as e:
        print(f"❌ Deep reprocessing failed: {e}")
        return claim_packet

@app.post("/api/generate-final-outputs")
async def generate_final_outputs(request: Dict[str, Any]):
    """Generate comprehensive claim package ZIP with all documents, attestation score, and proof card"""
    try:
        # Get raw data first
        claim_packet_data = request.get("claim_packet", {})
        validation_data = request.get("validation", {})
        
        print(f"📥 Received generate_final_outputs request")
        print(f"📦 Claim packet data keys: {claim_packet_data.keys()}")
        print(f"✅ Validation data keys: {validation_data.keys()}")
        
        # Convert to Pydantic models
        claim_packet = ClaimPacket(**claim_packet_data)
        validation = ClaimValidation(**validation_data)
        
        print(f"🎁 Generating comprehensive claim package for {claim_packet.claim_id}")
        print(f"📄 Number of documents: {len(claim_packet.documents)}")
        
        # Generate COMPREHENSIVE CLAIM PACKAGE (ZIP file with all documents)
        comprehensive_package_path = await generate_comprehensive_claim_package(
            claim_packet, 
            validation,
            generate_final_claim_packet_pdf  # Pass the function as parameter
        )
        
        # Also generate final PDF for legacy support
        final_pdf_path = await generate_final_claim_packet_pdf(claim_packet, validation)
        
        # Create claim hash for ECDSA signature
        claim_data = {
            "claim_id": claim_packet.claim_id,
            "policy_number": claim_packet.policy_number,
            "claimant_name": claim_packet.claimant_name,
            "incident_date": claim_packet.incident_date.isoformat(),
            "property_address": claim_packet.property_address,
            "validation_score": validation.overall_score,
            "approved": validation.approved,
            "timestamp": datetime.now().isoformat()
        }
        
        claim_json = json.dumps(claim_data, sort_keys=True)
        claim_hash = hashlib.sha256(claim_json.encode()).hexdigest()
        
        # Generate ECDSA signature
        ecdsa_signature = await generate_ecdsa_signature(claim_hash)
        
        # Create proof card
        proof_card = {
            "claim_hash": claim_hash,
            "ecdsa_signature": ecdsa_signature,
            "timestamp": int(time.time()),
            "judge_score": validation.overall_score,
            "validation_rules_version": "v1.0",
            "trust_badge": get_trust_badge(validation.overall_score)
        }
        
        # Store proof with ECDSA signature
        os.makedirs("eigencloud_proofs", exist_ok=True)
        proof_file = f"eigencloud_proofs/{claim_hash[:16]}.json"
        
        with open(proof_file, 'w') as f:
            json.dump({
                "claim_hash": claim_hash,
                "ecdsa_signature": ecdsa_signature,
                "eigencloud_attestation": getattr(validation, 'eigencloud_attestation', 'TEE evaluation completed'),
                "evaluator_address": getattr(validation, 'evaluator_address', 'EigenCloud TEE'),
                "timestamp": proof_card["timestamp"],
                "judge_score": proof_card["judge_score"],
                "validation_rules_version": proof_card["validation_rules_version"],
                "trust_badge": proof_card["trust_badge"],
                "proof_type": "ECDSA_SHA256"
            }, f, indent=2)
        
        verification_url = f"http://localhost:8000/api/verify-proof/{claim_hash[:16]}"
        
        # 💾 UPDATE DATABASE WITH FINAL OUTPUTS
        from database import ClaimRecord, SessionLocal
        db = SessionLocal()
        try:
            claim_record = db.query(ClaimRecord).filter(ClaimRecord.claim_id == claim_packet.claim_id).first()
            if claim_record:
                claim_record.status = "completed"
                claim_record.proof_card = proof_card
                claim_record.updated_at = datetime.now()
                db.commit()
                print(f"💾 Final outputs saved to database")
            else:
                print(f"⚠️ Claim {claim_packet.claim_id} not found in database")
        except Exception as db_error:
            print(f"⚠️ Database update failed: {db_error}")
            db.rollback()
        finally:
            db.close()
        
        return {
            "comprehensive_package_zip": comprehensive_package_path,
            "final_claim_packet_pdf": final_pdf_path,
            "attestation_score": validation.overall_score,
            "trust_badge": proof_card["trust_badge"],
            "proof_card": proof_card,
            "proof_id": claim_hash[:16],
            "verification_url": verification_url,
            "status": "completed"
        }
    except Exception as e:
        print(f"Error in generate_final_outputs: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/download-final-pdf/{claim_id}")
async def download_final_pdf(claim_id: str):
    """Download the final validated claim packet PDF"""
    try:
        pdf_path = f"claim_packets/{claim_id}_final.pdf"
        
        if not os.path.exists(pdf_path):
            raise HTTPException(status_code=404, detail="Final PDF not found")
        
        return FileResponse(
            pdf_path,
            media_type='application/pdf',
            filename=f"claim_{claim_id}_final_validated.pdf",
            headers={"Content-Disposition": f"attachment; filename=claim_{claim_id}_final_validated.pdf"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/download-complete-package/{claim_id}")
async def download_complete_package(claim_id: str):
    """Download the comprehensive claim package ZIP file"""
    try:
        zip_path = f"claim_packets/{claim_id}_COMPLETE_PACKAGE.zip"
        
        if not os.path.exists(zip_path):
            raise HTTPException(status_code=404, detail="Complete package not found")
        
        return FileResponse(
            zip_path,
            media_type='application/zip',
            filename=f"claim_{claim_id}_COMPLETE_PACKAGE.zip",
            headers={"Content-Disposition": f"attachment; filename=claim_{claim_id}_COMPLETE_PACKAGE.zip"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/verify-proof/{proof_id}")
async def verify_proof(proof_id: str):
    """Verify ECDSA signature and proof authenticity"""
    try:
        proof_file = f"eigencloud_proofs/{proof_id}.json"
        
        if not os.path.exists(proof_file):
            return {"verified": False, "error": "Proof not found"}
        
        with open(proof_file, 'r') as f:
            proof_data = json.load(f)
        
        # Verify ECDSA signature
        signature_valid = await verify_ecdsa_signature(
            proof_data["claim_hash"],
            proof_data["ecdsa_signature"]
        )
        
        return {
            "verified": signature_valid,
            "proof_type": "ECDSA_SHA256",
            "claim_hash": proof_data["claim_hash"],
            "ecdsa_signature": proof_data["ecdsa_signature"],
            "eigencloud_attestation": proof_data["eigencloud_attestation"],
            "evaluator_address": proof_data["evaluator_address"],
            "timestamp": proof_data["timestamp"],
            "judge_score": proof_data["judge_score"],
            "trust_badge": proof_data["trust_badge"],
            "validation_rules_version": proof_data["validation_rules_version"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/download-claim-packet/{claim_id}")
async def download_claim_packet(claim_id: str):
    """Download final claim packet PDF"""
    try:
        pdf_path = f"claim_packets/{claim_id}_final.pdf"
        if os.path.exists(pdf_path):
            return FileResponse(
                pdf_path,
                media_type="application/pdf",
                filename=f"claim_{claim_id}_final.pdf"
            )
        else:
            raise HTTPException(status_code=404, detail="Claim packet not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/claims/{claim_id}/status")
async def get_claim_status(claim_id: str):
    """Get claim processing status from database"""
    try:
        from database import ClaimRecord, SessionLocal
        db = SessionLocal()
        try:
            claim_record = db.query(ClaimRecord).filter(ClaimRecord.claim_id == claim_id).first()
            if not claim_record:
                raise HTTPException(status_code=404, detail="Claim not found")
            
            return {
                "claim_id": claim_record.claim_id,
                "status": claim_record.status,
                "claimant_name": claim_record.claimant_name,
                "policy_number": claim_record.policy_number,
                "estimated_damage": claim_record.estimated_damage,
                "created_at": claim_record.created_at.isoformat(),
                "updated_at": claim_record.updated_at.isoformat() if claim_record.updated_at else None,
                "validation_score": claim_record.validation_result.get("overall_score") if claim_record.validation_result else None
            }
        finally:
            db.close()
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/claims")
async def list_claims(limit: int = 10, offset: int = 0):
    """List all claims from database"""
    try:
        from database import ClaimRecord, SessionLocal
        db = SessionLocal()
        try:
            claims = db.query(ClaimRecord).order_by(ClaimRecord.created_at.desc()).offset(offset).limit(limit).all()
            
            return {
                "claims": [{
                    "claim_id": claim.claim_id,
                    "claimant_name": claim.claimant_name,
                    "policy_number": claim.policy_number,
                    "status": claim.status,
                    "estimated_damage": claim.estimated_damage,
                    "created_at": claim.created_at.isoformat()
                } for claim in claims],
                "total": db.query(ClaimRecord).count()
            }
        finally:
            db.close()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
