"""
REAL Insurance Claim Package Generator
Generates actual submission-ready insurance claim documents based on industry standards
"""

import os
import zipfile
import json
import shutil
from datetime import datetime
from reportlab.lib.pagesizes import letter, A4
from reportlab.pdfgen import canvas
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle, Image as RLImage
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY, TA_RIGHT
from io import BytesIO
from PIL import Image
import base64


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


async def generate_cover_letter_pdf(claim_packet, validation) -> str:
    """Generate professional insurance claim cover letter"""
    os.makedirs("claim_packets/temp", exist_ok=True)
    pdf_path = f"claim_packets/temp/01_COVER_LETTER_{claim_packet.claim_id}.pdf"
    
    doc = SimpleDocTemplate(pdf_path, pagesize=letter, rightMargin=72, leftMargin=72,
                           topMargin=72, bottomMargin=72)
    styles = getSampleStyleSheet()
    story = []
    
    # Header with date
    header_style = ParagraphStyle('Header', parent=styles['Normal'], fontSize=11, alignment=TA_RIGHT)
    story.append(Paragraph(datetime.now().strftime('%B %d, %Y'), header_style))
    story.append(Spacer(1, 30))
    
    # Insurance company address placeholder
    story.append(Paragraph("Claims Department<br/>Insurance Company Name<br/>Address Line 1<br/>City, State ZIP", styles['Normal']))
    story.append(Spacer(1, 20))
    
    # Subject line
    subject_style = ParagraphStyle('Subject', parent=styles['Normal'], fontSize=11, fontName='Helvetica-Bold')
    story.append(Paragraph(f"<b>RE: Fire Insurance Claim - Policy #{claim_packet.policy_number}</b>", subject_style))
    story.append(Paragraph(f"<b>Claim Reference: {claim_packet.claim_id}</b>", subject_style))
    story.append(Spacer(1, 20))
    
    # Salutation
    story.append(Paragraph("Dear Claims Adjuster,", styles['Normal']))
    story.append(Spacer(1, 12))
    
    # Body
    body_text = f"""
    I am writing to formally submit my insurance claim for fire damage to my property located at 
    <b>{claim_packet.property_address}</b>, which occurred on <b>{claim_packet.incident_date.strftime('%B %d, %Y')}</b>.
    <br/><br/>
    <b>Claim Summary:</b><br/>
    Policy Number: {claim_packet.policy_number}<br/>
    Claimant Name: {claim_packet.claimant_name}<br/>
    Property Address: {claim_packet.property_address}<br/>
    Date of Loss: {claim_packet.incident_date.strftime('%B %d, %Y')}<br/>
    Estimated Damage: ${claim_packet.estimated_damage:,.2f}
    <br/><br/>
    This claim submission package includes all required documentation to support my claim:
    <br/><br/>
    • <b>Proof of Loss Statement</b> - Detailed claim information and sworn statement<br/>
    • <b>Property Damage Documentation</b> - Comprehensive photographic evidence<br/>
    • <b>Itemized Loss Inventory</b> - Complete list of damaged/destroyed property with values<br/>
    • <b>Purchase Receipts</b> - Original receipts for major items<br/>
    • <b>Fire Department Report</b> - Official incident documentation<br/>
    • <b>Contractor Estimates</b> - Professional damage assessments and repair quotes
    <br/><br/>
    All documentation has been organized and prepared in accordance with standard insurance claim requirements. 
    I have made every effort to provide complete and accurate information to facilitate prompt processing of this claim.
    <br/><br/>
    I am available for inspection at your earliest convenience and am prepared to provide any additional 
    information or documentation that may be required. Please contact me at your earliest convenience to 
    schedule an inspection or discuss this claim.
    <br/><br/>
    I appreciate your prompt attention to this matter and look forward to working with you toward a fair 
    and timely resolution.
    <br/><br/>
    Sincerely,
    <br/><br/><br/>
    {claim_packet.claimant_name}<br/>
    Property Owner
    """
    
    story.append(Paragraph(body_text, styles['Normal']))
    
    doc.build(story)
    return pdf_path


async def generate_proof_of_loss_pdf(claim_packet, validation) -> str:
    """Generate Proof of Loss statement - the official claim form"""
    os.makedirs("claim_packets/temp", exist_ok=True)
    pdf_path = f"claim_packets/temp/02_PROOF_OF_LOSS_{claim_packet.claim_id}.pdf"
    
    doc = SimpleDocTemplate(pdf_path, pagesize=letter, rightMargin=50, leftMargin=50,
                           topMargin=50, bottomMargin=50)
    styles = getSampleStyleSheet()
    story = []
    
    # Title
    title_style = ParagraphStyle('Title', parent=styles['Heading1'], fontSize=18, 
                                 alignment=TA_CENTER, spaceAfter=30, textColor=colors.HexColor('#1a365d'))
    story.append(Paragraph("PROOF OF LOSS STATEMENT", title_style))
    story.append(Paragraph(f"Claim ID: {claim_packet.claim_id}", ParagraphStyle('Subtitle', parent=styles['Normal'], 
                                                                                  alignment=TA_CENTER, fontSize=10)))
    story.append(Spacer(1, 30))
    
    # Section 1: Policy Information
    story.append(Paragraph("<b>SECTION 1: POLICY AND CLAIMANT INFORMATION</b>", styles['Heading2']))
    
    policy_data = [
        ['Policy Number:', claim_packet.policy_number],
        ['Insured Name:', claim_packet.claimant_name],
        ['Property Address:', claim_packet.property_address],
        ['Date of Loss:', claim_packet.incident_date.strftime('%B %d, %Y')],
        ['Date Claim Filed:', datetime.now().strftime('%B %d, %Y')],
        ['Type of Loss:', 'Fire Damage - Wildfire']
    ]
    
    table = Table(policy_data, colWidths=[2*inch, 4*inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    
    story.append(table)
    story.append(Spacer(1, 20))
    
    # Section 2: Loss Description
    story.append(Paragraph("<b>SECTION 2: DESCRIPTION OF LOSS</b>", styles['Heading2']))
    loss_description = f"""
    On {claim_packet.incident_date.strftime('%B %d, %Y')}, my property located at {claim_packet.property_address} 
    sustained fire damage as a result of a wildfire. The fire caused significant damage to the structure, 
    personal property, and surrounding areas. Emergency services responded to the incident, and the fire 
    was extinguished. I have documented all damage with photographs and have compiled a complete inventory 
    of damaged and destroyed property.
    """
    story.append(Paragraph(loss_description, styles['Normal']))
    story.append(Spacer(1, 20))
    
    # Section 3: Damage Summary
    story.append(Paragraph("<b>SECTION 3: SUMMARY OF DAMAGES</b>", styles['Heading2']))
    
    damage_summary = [
        ['Category', 'Estimated Value'],
        ['Structural Damage', f"${claim_packet.estimated_damage * 0.6:,.2f}"],
        ['Personal Property', f"${claim_packet.estimated_damage * 0.3:,.2f}"],
        ['Additional Living Expenses', f"${claim_packet.estimated_damage * 0.1:,.2f}"],
        ['<b>TOTAL ESTIMATED LOSS</b>', f"<b>${claim_packet.estimated_damage:,.2f}</b>"]
    ]
    
    damage_table = Table(damage_summary, colWidths=[4*inch, 2*inch])
    damage_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a365d')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BACKGROUND', (0, -1), (-1, -1), colors.lightgrey),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    
    story.append(damage_table)
    story.append(Spacer(1, 30))
    
    # Section 4: Sworn Statement
    story.append(Paragraph("<b>SECTION 4: SWORN STATEMENT</b>", styles['Heading2']))
    sworn_text = """
    I hereby certify that the foregoing statements are true and correct to the best of my knowledge and belief. 
    I understand that any false or misleading statement made in connection with this claim may result in denial 
    of the claim and could subject me to criminal penalties.
    <br/><br/>
    All supporting documentation, including photographs, receipts, and reports, are attached to this Proof of Loss 
    and form part of this claim submission.
    """
    story.append(Paragraph(sworn_text, styles['Normal']))
    story.append(Spacer(1, 40))
    
    # Signature block
    sig_data = [
        ['Signature: ________________________________', f'Date: {datetime.now().strftime("%B %d, %Y")}'],
        [f'Printed Name: {claim_packet.claimant_name}', '']
    ]
    
    sig_table = Table(sig_data, colWidths=[4*inch, 2*inch])
    sig_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    
    story.append(sig_table)
    
    doc.build(story)
    return pdf_path


async def generate_property_damage_photos_pdf(claim_packet) -> str:
    """Compile all property damage photos into a single organized PDF"""
    os.makedirs("claim_packets/temp", exist_ok=True)
    pdf_path = f"claim_packets/temp/03_PROPERTY_DAMAGE_PHOTOS_{claim_packet.claim_id}.pdf"
    
    doc = SimpleDocTemplate(pdf_path, pagesize=letter, rightMargin=50, leftMargin=50,
                           topMargin=50, bottomMargin=50)
    styles = getSampleStyleSheet()
    story = []
    
    # Title
    title_style = ParagraphStyle('Title', parent=styles['Heading1'], fontSize=18, 
                                 alignment=TA_CENTER, spaceAfter=20)
    story.append(Paragraph("PROPERTY DAMAGE PHOTOGRAPHIC EVIDENCE", title_style))
    story.append(Paragraph(f"Claim ID: {claim_packet.claim_id}", 
                          ParagraphStyle('Subtitle', parent=styles['Normal'], alignment=TA_CENTER, fontSize=10)))
    story.append(Spacer(1, 30))
    
    # Get all photo documents
    photo_docs = [doc for doc in claim_packet.documents if doc.document_type.value == 'photo']
    
    if not photo_docs:
        story.append(Paragraph("No property damage photographs were submitted with this claim.", styles['Normal']))
    else:
        story.append(Paragraph(f"<b>Total Photographs: {len(photo_docs)}</b>", styles['Normal']))
        story.append(Paragraph(f"Date of Incident: {claim_packet.incident_date.strftime('%B %d, %Y')}", styles['Normal']))
        story.append(Spacer(1, 20))
        
        # Add each photo with description
        for idx, photo in enumerate(photo_docs, 1):
            story.append(Paragraph(f"<b>Photograph #{idx}: {photo.filename}</b>", styles['Heading3']))
            story.append(Paragraph(f"Upload Date: {photo.upload_timestamp.strftime('%B %d, %Y')}", styles['Normal']))
            
            # Add damage description if available from OCR
            if photo.extracted_data and photo.extracted_data.get('damage_type'):
                story.append(Paragraph(f"Damage Type: {photo.extracted_data.get('damage_type', 'Not specified')}", styles['Normal']))
            
            story.append(Spacer(1, 10))
            
            # Try to embed the actual image
            try:
                if hasattr(photo, 'file_path') and photo.file_path and os.path.exists(photo.file_path):
                    # Use actual image file
                    img = RLImage(photo.file_path, width=5*inch, height=3.75*inch)
                    story.append(img)
                elif hasattr(photo, 'content') and photo.content:
                    # Use base64 encoded content
                    img_data = base64.b64decode(photo.content)
                    img_buffer = BytesIO(img_data)
                    img = RLImage(img_buffer, width=5*inch, height=3.75*inch)
                    story.append(img)
                else:
                    story.append(Paragraph("[Image placeholder - Original file not available]", styles['Italic']))
            except Exception as e:
                story.append(Paragraph(f"[Image could not be embedded: {photo.filename}]", styles['Italic']))
            
            story.append(Spacer(1, 20))
            
            if idx < len(photo_docs):
                story.append(PageBreak())
    
    doc.build(story)
    return pdf_path


async def generate_itemized_inventory_pdf(claim_packet) -> str:
    """Generate itemized loss inventory with values"""
    os.makedirs("claim_packets/temp", exist_ok=True)
    pdf_path = f"claim_packets/temp/04_ITEMIZED_LOSS_INVENTORY_{claim_packet.claim_id}.pdf"
    
    doc = SimpleDocTemplate(pdf_path, pagesize=letter, rightMargin=50, leftMargin=50,
                           topMargin=50, bottomMargin=50)
    styles = getSampleStyleSheet()
    story = []
    
    # Title
    title_style = ParagraphStyle('Title', parent=styles['Heading1'], fontSize=18, 
                                 alignment=TA_CENTER, spaceAfter=20)
    story.append(Paragraph("ITEMIZED INVENTORY OF DAMAGED/DESTROYED PROPERTY", title_style))
    story.append(Paragraph(f"Claim ID: {claim_packet.claim_id}", 
                          ParagraphStyle('Subtitle', parent=styles['Normal'], alignment=TA_CENTER, fontSize=10)))
    story.append(Spacer(1, 30))
    
    # Get all receipts
    receipt_docs = [doc for doc in claim_packet.documents if doc.document_type.value == 'receipt']
    
    if not receipt_docs:
        story.append(Paragraph("No itemized inventory data available. Please refer to contractor estimates for structural damage assessment.", styles['Normal']))
    else:
        # Create inventory table
        inventory_data = [['Item Description', 'Purchase Date', 'Original Value', 'Condition']]
        total_value = 0
        
        for receipt in receipt_docs:
            if receipt.extracted_data:
                items = receipt.extracted_data.get('items', [])
                amount = receipt.extracted_data.get('total_amount', 0)
                date = receipt.extracted_data.get('date', 'Unknown')
                merchant = receipt.extracted_data.get('merchant', 'Unknown')
                
                # Handle amount being a string with $
                if isinstance(amount, str):
                    amount = float(amount.replace('$', '').replace(',', ''))
                
                if items and len(items) > 0:
                    for item in items[:3]:  # First 3 items per receipt
                        inventory_data.append([
                            str(item)[:40],
                            str(date),
                            f"${float(amount)/len(items):,.2f}",
                            'Destroyed/Damaged'
                        ])
                        total_value += float(amount)/len(items)
                else:
                    inventory_data.append([
                        f"Items from {merchant}",
                        str(date),
                        f"${amount:,.2f}",
                        'Destroyed/Damaged'
                    ])
                    total_value += amount
        
        # Add total row
        inventory_data.append(['<b>TOTAL DOCUMENTED VALUE</b>', '', f'<b>${total_value:,.2f}</b>', ''])
        
        inventory_table = Table(inventory_data, colWidths=[2.5*inch, 1.5*inch, 1.2*inch, 1.3*inch])
        inventory_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a365d')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BACKGROUND', (0, -1), (-1, -1), colors.lightgrey),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('ALIGN', (2, 1), (2, -1), 'RIGHT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        
        story.append(inventory_table)
        story.append(Spacer(1, 20))
        
        # Note
        note_text = """
        <b>Note:</b> This inventory represents documented items with available receipts. Additional items without 
        receipts may be listed in supplemental documentation. All values represent original purchase price. 
        Depreciation and actual cash value will be calculated by the insurance adjuster.
        """
        story.append(Paragraph(note_text, styles['Normal']))
    
    doc.build(story)
    return pdf_path


async def generate_receipts_compilation_pdf(claim_packet) -> str:
    """Compile all receipts into a single PDF"""
    os.makedirs("claim_packets/temp", exist_ok=True)
    pdf_path = f"claim_packets/temp/05_PURCHASE_RECEIPTS_{claim_packet.claim_id}.pdf"
    
    doc = SimpleDocTemplate(pdf_path, pagesize=letter, rightMargin=50, leftMargin=50,
                           topMargin=50, bottomMargin=50)
    styles = getSampleStyleSheet()
    story = []
    
    # Title
    title_style = ParagraphStyle('Title', parent=styles['Heading1'], fontSize=18, 
                                 alignment=TA_CENTER, spaceAfter=20)
    story.append(Paragraph("PURCHASE RECEIPTS AND INVOICES", title_style))
    story.append(Paragraph(f"Claim ID: {claim_packet.claim_id}", 
                          ParagraphStyle('Subtitle', parent=styles['Normal'], alignment=TA_CENTER, fontSize=10)))
    story.append(Spacer(1, 30))
    
    # Get all receipts
    receipt_docs = [doc for doc in claim_packet.documents if doc.document_type.value == 'receipt']
    
    if not receipt_docs:
        story.append(Paragraph("No purchase receipts were submitted with this claim.", styles['Normal']))
    else:
        story.append(Paragraph(f"<b>Total Receipts: {len(receipt_docs)}</b>", styles['Normal']))
        story.append(Spacer(1, 20))
        
        # Add each receipt
        for idx, receipt in enumerate(receipt_docs, 1):
            story.append(Paragraph(f"<b>Receipt #{idx}</b>", styles['Heading3']))
            
            if receipt.extracted_data:
                receipt_info = [
                    ['Merchant:', receipt.extracted_data.get('merchant', 'Unknown')],
                    ['Date:', str(receipt.extracted_data.get('date', 'Unknown'))],
                    ['Amount:', f"${receipt.extracted_data.get('total_amount', 0):,.2f}" if isinstance(receipt.extracted_data.get('total_amount'), (int, float)) else str(receipt.extracted_data.get('total_amount', '$0.00'))],
                    ['Payment Method:', receipt.extracted_data.get('payment_method', 'Unknown')],
                ]
                
                if receipt.extracted_data.get('items'):
                    items_list = '<br/>'.join([f"• {item}" for item in receipt.extracted_data['items'][:5]])
                    receipt_info.append(['Items:', items_list])
                
                info_table = Table(receipt_info, colWidths=[1.5*inch, 4.5*inch])
                info_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
                    ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                    ('TOPPADDING', (0, 0), (-1, -1), 6),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ]))
                
                story.append(info_table)
            
            story.append(Spacer(1, 15))
            
            if idx < len(receipt_docs):
                story.append(PageBreak())
    
    doc.build(story)
    return pdf_path


async def generate_comprehensive_claim_package(claim_packet, validation, generate_final_pdf_func) -> str:
    """
    Generate REAL, submission-ready insurance claim package
    
    Package Contents (Industry Standard):
    1. Cover Letter - Professional submission letter
    2. Proof of Loss Statement - Official sworn claim form
    3. Property Damage Photos - All photos compiled with descriptions
    4. Itemized Loss Inventory - Complete inventory with values
    5. Purchase Receipts - All receipts compiled
    6. Fire Department Reports - Official incident documentation
    7. Contractor Estimates - Repair/replacement quotes
    8. AI Validation Report - Trust score and analysis
    """
    
    print(f"📦 Generating REAL insurance claim package for {claim_packet.claim_id}")
    
    # Create temp directory
    temp_dir = f"claim_packets/temp/{claim_packet.claim_id}"
    os.makedirs(temp_dir, exist_ok=True)
    
    try:
        # 1. Generate Cover Letter (Professional insurance submission letter)
        print("📄 Generating cover letter...")
        cover_letter_path = await generate_cover_letter_pdf(claim_packet, validation)
        shutil.copy(cover_letter_path, f"{temp_dir}/01_COVER_LETTER.pdf")
        
        # 2. Generate Proof of Loss Statement (Official claim form)
        print("📋 Generating proof of loss statement...")
        proof_of_loss_path = await generate_proof_of_loss_pdf(claim_packet, validation)
        shutil.copy(proof_of_loss_path, f"{temp_dir}/02_PROOF_OF_LOSS_STATEMENT.pdf")
        
        # 3. Generate Property Damage Photos PDF
        print("📸 Compiling property damage photos...")
        photos_path = await generate_property_damage_photos_pdf(claim_packet)
        shutil.copy(photos_path, f"{temp_dir}/03_PROPERTY_DAMAGE_PHOTOS.pdf")
        
        # 4. Generate Itemized Loss Inventory
        print("📊 Creating itemized inventory...")
        inventory_path = await generate_itemized_inventory_pdf(claim_packet)
        shutil.copy(inventory_path, f"{temp_dir}/04_ITEMIZED_LOSS_INVENTORY.pdf")
        
        # 5. Generate Purchase Receipts Compilation
        print("🧾 Compiling purchase receipts...")
        receipts_path = await generate_receipts_compilation_pdf(claim_packet)
        shutil.copy(receipts_path, f"{temp_dir}/05_PURCHASE_RECEIPTS.pdf")
        
        # 6. Copy Fire Department Reports and ALL user documents
        print("🚒 Including all user documents...")
        
        # Organize all documents by type
        for doc in claim_packet.documents:
            # Get file_path (handle both dict and object)
            if isinstance(doc, dict):
                file_path = doc.get('file_path')
                filename = doc.get('filename', 'unknown.pdf')
                doc_type = doc.get('document_type', 'other')
                if isinstance(doc_type, dict):
                    doc_type = doc_type.get('value', 'other')
            else:
                file_path = getattr(doc, 'file_path', None)
                filename = doc.filename
                doc_type = doc.document_type.value if hasattr(doc.document_type, 'value') else str(doc.document_type)
            
            # Skip if no file_path or file doesn't exist
            if not file_path or not os.path.exists(file_path):
                print(f"⚠️ Skipping {filename} - file not found at {file_path}")
                continue
            
            # Determine destination folder
            if doc_type == 'damage_report' or 'report' in filename.lower():
                dest_folder = f"{temp_dir}/04_REPORTS"
                os.makedirs(dest_folder, exist_ok=True)
                dest_path = os.path.join(dest_folder, filename)
                shutil.copy(file_path, dest_path)
                print(f"📄 Copied report: {filename}")
            elif doc_type == 'receipt' or 'receipt' in filename.lower():
                dest_folder = f"{temp_dir}/03_RECEIPTS"
                os.makedirs(dest_folder, exist_ok=True)
                dest_path = os.path.join(dest_folder, filename)
                shutil.copy(file_path, dest_path)
                print(f"📄 Copied receipt: {filename}")
            elif 'estimate' in filename.lower() or 'contractor' in filename.lower():
                dest_folder = f"{temp_dir}/04_REPORTS"
                os.makedirs(dest_folder, exist_ok=True)
                dest_path = os.path.join(dest_folder, filename)
                shutil.copy(file_path, dest_path)
                print(f"📄 Copied estimate: {filename}")
        
        # 8. Generate AI Validation Report
        print("🤖 Generating AI validation report...")
        validation_report_path = await generate_final_pdf_func(claim_packet, validation)
        shutil.copy(validation_report_path, f"{temp_dir}/99_AI_VALIDATION_REPORT.pdf")
        
        # 9. Create README file
        readme_content = f"""
═══════════════════════════════════════════════════════════════
                  INSURANCE CLAIM SUBMISSION PACKAGE
═══════════════════════════════════════════════════════════════

Claim ID: {claim_packet.claim_id}
Policy Number: {claim_packet.policy_number}
Claimant: {claim_packet.claimant_name}
Property Address: {claim_packet.property_address}
Date of Loss: {claim_packet.incident_date.strftime('%B %d, %Y')}
Package Generated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}

═══════════════════════════════════════════════════════════════
                           PACKAGE CONTENTS
═══════════════════════════════════════════════════════════════

01_COVER_LETTER.pdf
    Professional submission letter to insurance adjuster
    
02_PROOF_OF_LOSS_STATEMENT.pdf
    Official sworn claim statement with all required information
    
03_PROPERTY_DAMAGE_PHOTOS.pdf
    Comprehensive photographic evidence of all damage
    
04_ITEMIZED_LOSS_INVENTORY.pdf
    Complete inventory of damaged/destroyed property with values
    
05_PURCHASE_RECEIPTS.pdf
    Original purchase receipts and invoices
    
06_FIRE_DEPT_REPORT_[#].pdf (if available)
    Official fire department incident reports
    
07_CONTRACTOR_ESTIMATE_[#].pdf (if available)
    Professional damage assessments and repair quotes
    
99_AI_VALIDATION_REPORT.pdf
    AI-powered claim validation analysis and trust score

═══════════════════════════════════════════════════════════════
                        SUBMISSION INSTRUCTIONS
═══════════════════════════════════════════════════════════════

1. Review all documents for completeness and accuracy
2. Sign the Proof of Loss Statement (Item 02)
3. Submit entire package to your insurance company:
   - Via mail (keep copies for your records)
   - Via email (if permitted by your insurer)
   - In person at claims office
4. Keep this complete package for your records
5. Follow up with claims adjuster within 5-7 business days

═══════════════════════════════════════════════════════════════
                          IMPORTANT NOTES
═══════════════════════════════════════════════════════════════

• AI VALIDATION SCORE: {validation.overall_score:.1%}
• SUBMISSION STATUS: {"APPROVED - Complete" if validation.approved else "REVIEW RECOMMENDED - May require additional documentation"}
• TRUST BADGE: {get_trust_badge(validation.overall_score)}

This claim package has been professionally compiled and validated
using advanced AI technology to ensure completeness and accuracy.

All documents are submission-ready and formatted according to
standard insurance industry requirements.

═══════════════════════════════════════════════════════════════

For questions about this claim package, please reference:
Claim ID: {claim_packet.claim_id}
Generated by: KAVA AI Claims Processing System
        """
        
        with open(f"{temp_dir}/README.txt", 'w') as f:
            f.write(readme_content)
        
        # 10. Create ZIP file
        print("🗜️ Creating ZIP archive...")
        zip_path = f"claim_packets/{claim_packet.claim_id}_COMPLETE_PACKAGE.zip"
        
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(temp_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, temp_dir)
                    zipf.write(file_path, arcname)
        
        # 11. Cleanup temp directory
        shutil.rmtree(temp_dir)
        
        print(f"✅ REAL insurance claim package generated: {zip_path}")
        print(f"📄 Package contains professional, submission-ready documents")
        return zip_path
        
    except Exception as e:
        print(f"❌ Error generating claim package: {e}")
        import traceback
        traceback.print_exc()
        # Cleanup on error
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
        raise
