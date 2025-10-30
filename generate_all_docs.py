#!/usr/bin/env python3
"""Generate all realistic wildfire claim documents"""
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
import os

os.chdir('/Users/rimjhim/Desktop/SELFPROJECTS/Kava- testing/test_realistic_claim')

# 1. Insurance Policy Document
print("Creating insurance policy...")
c = canvas.Canvas("04_insurance_policy.pdf", pagesize=letter)
width, height = letter

c.setFont("Helvetica-Bold", 18)
c.drawString(2*inch, height - 1*inch, "HOMEOWNERS INSURANCE POLICY")

c.setFont("Helvetica", 11)
c.drawString(1*inch, height - 1.5*inch, "Policy Number: HO-2025-891234-CA")
c.drawString(1*inch, height - 1.7*inch, "Policy Holder: Sarah Martinez")
c.drawString(1*inch, height - 1.9*inch, "Property Address: 2847 Redwood Drive, Los Gatos, CA 95032")
c.drawString(1*inch, height - 2.1*inch, "Effective Date: January 1, 2025")
c.drawString(1*inch, height - 2.3*inch, "Expiration Date: January 1, 2026")

c.setFont("Helvetica-Bold", 12)
c.drawString(1*inch, height - 2.7*inch, "COVERAGE SUMMARY")
c.setFont("Helvetica", 10)
c.drawString(1.3*inch, height - 3*inch, "• Dwelling Coverage: $450,000")
c.drawString(1.3*inch, height - 3.2*inch, "• Personal Property: $225,000")
c.drawString(1.3*inch, height - 3.4*inch, "• Additional Living Expenses: $90,000")
c.drawString(1.3*inch, height - 3.6*inch, "• Liability: $500,000")
c.drawString(1.3*inch, height - 3.8*inch, "• Deductible: $2,500")

c.setFont("Helvetica-Bold", 11)
c.drawString(1*inch, height - 4.2*inch, "WILDFIRE COVERAGE: INCLUDED")
c.setFont("Helvetica", 9)
c.drawString(1.3*inch, height - 4.4*inch, "This policy includes full coverage for wildfire damage,")
c.drawString(1.3*inch, height - 4.6*inch, "including smoke damage, ash damage, and evacuation expenses.")

c.setFont("Helvetica", 8)
c.drawString(1*inch, height - 9*inch, "California Insurance Company • License #CA-88234 • P.O. Box 9000, Sacramento, CA 95812")

c.save()
print("✅ Created 04_insurance_policy.pdf")

# 2. Fire Department Report
print("Creating fire department report...")
c = canvas.Canvas("05_fire_dept_incident_report.pdf", pagesize=letter)

c.setFont("Helvetica-Bold", 16)
c.drawString(1.5*inch, height - 0.8*inch, "SANTA CLARA COUNTY FIRE DEPARTMENT")
c.setFont("Helvetica", 10)
c.drawString(2.2*inch, height - 1*inch, "INCIDENT REPORT")

c.line(0.75*inch, height - 1.2*inch, 7.5*inch, height - 1.2*inch)

c.setFont("Helvetica-Bold", 11)
c.drawString(1*inch, height - 1.5*inch, "INCIDENT INFORMATION")
c.setFont("Helvetica", 10)
c.drawString(1*inch, height - 1.8*inch, "Incident Number: SCF-2025-08-15-0842")
c.drawString(1*inch, height - 2*inch, "Date of Incident: August 15, 2025")
c.drawString(1*inch, height - 2.2*inch, "Time Reported: 02:34 AM")
c.drawString(1*inch, height - 2.4*inch, "Time Arrived: 02:51 AM")
c.drawString(1*inch, height - 2.6*inch, "Incident Type: Structure Fire - Wildfire Related")

c.setFont("Helvetica-Bold", 11)
c.drawString(1*inch, height - 3*inch, "LOCATION")
c.setFont("Helvetica", 10)
c.drawString(1*inch, height - 3.3*inch, "Address: 2847 Redwood Drive, Los Gatos, CA 95032")
c.drawString(1*inch, height - 3.5*inch, "Nearest Intersection: Redwood Dr & Highway 17")
c.drawString(1*inch, height - 3.7*inch, "District: Los Gatos Hills")

c.setFont("Helvetica-Bold", 11)
c.drawString(1*inch, height - 4.1*inch, "INCIDENT NARRATIVE")
c.setFont("Helvetica", 9)
narrative = [
    "Upon arrival, heavy smoke visible from structure. Wildfire advancing from",
    "northeast approximately 0.5 miles from property. Embers observed landing on",
    "roof and igniting cedar shingles. Kitchen area sustained significant fire damage.",
    "Ceiling partially collapsed. Interior smoke and heat damage throughout first floor.",
    "",
    "Fire suppression initiated at 02:53 AM. Primary fire knocked down by 03:15 AM.",
    "Overhaul operations continued until 05:30 AM. Structure deemed unsafe for",
    "occupancy. Red tag posted. Residents evacuated to shelter at Los Gatos High School.",
    "",
    "Cause: Wildfire ember ignition of roof materials, extension to interior spaces.",
    "Origin: Exterior roof, southeast corner kitchen area.",
    "Estimated Damage: $85,000 - $120,000 (structure and contents)"
]

y = height - 4.4*inch
for line in narrative:
    c.drawString(1.2*inch, y, line)
    y -= 0.18*inch

c.setFont("Helvetica-Bold", 10)
y -= 0.3*inch
c.drawString(1*inch, y, "Responding Units: Engine 75, Engine 42, Truck 7, Battalion Chief 3")
c.drawString(1*inch, y - 0.2*inch, "Personnel: 18 firefighters on scene")

y -= 0.6*inch
c.drawString(1*inch, y, "Fire Captain: Robert Chen, Badge #1847")
c.drawString(1*inch, y - 0.2*inch, "Report Date: August 15, 2025")

c.save()
print("✅ Created 05_fire_dept_incident_report.pdf")

# 3. Contractor Estimate
print("Creating contractor estimate...")
c = canvas.Canvas("06_contractor_estimate.pdf", pagesize=letter)

c.setFont("Helvetica-Bold", 20)
c.drawString(1.5*inch, height - 0.9*inch, "RESTORATION ESTIMATE")

c.setFont("Helvetica", 10)
c.drawString(1*inch, height - 1.3*inch, "Bay Area Fire Restoration Services")
c.drawString(1*inch, height - 1.5*inch, "Licensed Contractor #945821")
c.drawString(1*inch, height - 1.7*inch, "2400 Walsh Ave, Santa Clara, CA 95051")
c.drawString(1*inch, height - 1.9*inch, "Phone: (408) 555-REST  Email: estimates@bayfirerestoration.com")

c.line(1*inch, height - 2.1*inch, 7*inch, height - 2.1*inch)

c.setFont("Helvetica-Bold", 11)
c.drawString(1*inch, height - 2.4*inch, "PROPERTY INFORMATION")
c.setFont("Helvetica", 10)
c.drawString(1*inch, height - 2.6*inch, "Owner: Sarah Martinez")
c.drawString(1*inch, height - 2.8*inch, "Property: 2847 Redwood Drive, Los Gatos, CA 95032")
c.drawString(1*inch, height - 3*inch, "Inspection Date: August 17, 2025")
c.drawString(1*inch, height - 3.2*inch, "Estimate Date: August 19, 2025")

c.setFont("Helvetica-Bold", 11)
c.drawString(1*inch, height - 3.6*inch, "SCOPE OF WORK")

# Work items table
y = height - 3.9*inch
c.setFont("Helvetica-Bold", 9)
c.drawString(1*inch, y, "ITEM")
c.drawString(5*inch, y, "COST")
y -= 0.2*inch

work_items = [
    ("Emergency Board-Up & Temporary Weatherproofing", "$2,850"),
    ("Smoke & Soot Damage Cleanup - Entire Structure", "$12,500"),
    ("Kitchen Demolition & Debris Removal", "$8,400"),
    ("Roof Replacement - 2,200 sq ft (fire-rated shingles)", "$28,600"),
    ("Kitchen Reconstruction (cabinets, flooring, drywall)", "$35,200"),
    ("Ceiling Repair & Replacement - First Floor", "$9,800"),
    ("Paint & Finish Work - Interior", "$7,600"),
    ("Electrical System Inspection & Repair", "$4,200"),
    ("HVAC Ductwork Cleaning & Filter Replacement", "$2,800"),
    ("Window Replacement (2 units - heat damaged)", "$3,400"),
]

c.setFont("Helvetica", 8.5)
for item, cost in work_items:
    c.drawString(1.2*inch, y, item)
    c.drawString(5*inch, y, cost)
    y -= 0.2*inch

# Total
y -= 0.3*inch
c.line(4*inch, y, 7*inch, y)
y -= 0.25*inch
c.setFont("Helvetica-Bold", 12)
c.drawString(3.5*inch, y, "TOTAL ESTIMATE:")
c.drawString(5*inch, y, "$115,350")

y -= 0.5*inch
c.setFont("Helvetica", 8)
c.drawString(1*inch, y, "Note: This estimate is for fire restoration work only. Additional structural engineering")
c.drawString(1*inch, y - 0.15*inch, "may be required. Estimate valid for 30 days. Work timeline: 8-12 weeks upon approval.")

y -= 0.6*inch
c.setFont("Helvetica-Bold", 9)
c.drawString(1*inch, y, "Prepared by: Michael Torres, Senior Estimator")
c.drawString(1*inch, y - 0.2*inch, "License #: 945821-A | IICRC Certified Fire Restoration Technician")

c.save()
print("✅ Created 06_contractor_estimate.pdf")

# 4. Additional damage photos description file
with open("07_additional_photos_README.txt", "w") as f:
    f.write("""ADDITIONAL DAMAGE PHOTOS

Photo 1: 01_kitchen_fire_damage.jpg
- Shows extensive fire damage to kitchen area
- Charred cabinets, melted appliances visible
- Ceiling collapse in corner
- Taken: August 15, 2025, 3:45 PM

Please upload this photo along with the PDFs for a complete claim submission.

These documents represent a realistic wildfire insurance claim with:
✅ Property damage photos (kitchen fire damage)
✅ Purchase receipts (Home Depot washer, Lowe's safety supplies)
✅ Fire department official incident report  
✅ Professional contractor damage estimate
✅ Insurance policy documentation

Total Documented Damages: ~$115,000
Receipt Total: ~$1,363
Expected AI Judge Score: 75-90% (well-documented claim)
""")

print("✅ Created 07_additional_photos_README.txt")
print("\n" + "="*60)
print("✅ REALISTIC WILDFIRE CLAIM TEST DOCUMENTS CREATED!")
print("="*60)
print("\nDocuments created in: test_realistic_claim/")
print("\n📁 Upload these to KAVA:")
print("  1. 01_kitchen_fire_damage.jpg - Property damage photo")
print("  2. 02_home_depot_receipt_washer.pdf - $1,073.86 receipt")
print("  3. 03_lowes_receipt_supplies.pdf - $289.38 receipt")
print("  4. 04_insurance_policy.pdf - Policy details")
print("  5. 05_fire_dept_incident_report.pdf - Official report")
print("  6. 06_contractor_estimate.pdf - $115,350 estimate")
print("\n💡 This realistic claim should score 75-90% based on completeness!")
