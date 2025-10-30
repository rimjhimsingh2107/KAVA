#!/usr/bin/env python3
"""Generate realistic Home Depot receipt PDF"""

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
import os

os.chdir('/Users/rimjhim/Desktop/SELFPROJECTS/Kava- testing/test_realistic_claim')

# Create PDF
c = canvas.Canvas("02_home_depot_receipt_washer.pdf", pagesize=letter)
width, height = letter

# Header
c.setFont("Helvetica-Bold", 24)
c.setFillColorRGB(0.95, 0.5, 0)  # Home Depot orange
c.drawString(1*inch, height - 1*inch, "THE HOME DEPOT")

c.setFont("Helvetica", 10)
c.setFillColorRGB(0, 0, 0)
c.drawString(1*inch, height - 1.3*inch, "Store #4287 - San Jose, CA")
c.drawString(1*inch, height - 1.5*inch, "1040 Blossom Hill Rd, San Jose, CA 95123")
c.drawString(1*inch, height - 1.7*inch, "Phone: (408) 225-5900")

# Receipt details
c.line(1*inch, height - 1.9*inch, 7*inch, height - 1.9*inch)

c.setFont("Helvetica-Bold", 12)
c.drawString(1*inch, height - 2.2*inch, "SALE RECEIPT")
c.setFont("Helvetica", 10)
c.drawString(1*inch, height - 2.4*inch, "Date: 08/18/2025  Time: 14:23")
c.drawString(1*inch, height - 2.6*inch, "Transaction #: 8821-4455-2301-8832")
c.drawString(1*inch, height - 2.8*inch, "Cashier: SARAH M.")

c.line(1*inch, height - 3*inch, 7*inch, height - 3*inch)

# Items
y_pos = height - 3.3*inch
c.setFont("Helvetica-Bold", 11)
c.drawString(1*inch, y_pos, "QTY  DESCRIPTION")
c.drawString(5.5*inch, y_pos, "PRICE")

y_pos -= 0.3*inch
c.setFont("Helvetica", 10)

items = [
    ("1", "Whirlpool 4.5 cu ft Top Load Washer", "899.00"),
    ("", "  Model: WTW5000DW - White", ""),
    ("", "  SKU: 1004792156", ""),
    ("1", "Washer Installation Kit", "24.99"),
    ("1", "4-Prong Dryer Cord", "18.97"),
    ("2", "Laundry Detergent - Tide HE 150oz", "19.99"),
]

for qty, desc, price in items:
    c.drawString(1*inch, y_pos, qty)
    c.drawString(1.5*inch, y_pos, desc)
    if price:
        c.drawString(5.5*inch, y_pos, f"${price}")
    y_pos -= 0.25*inch

# Totals
y_pos -= 0.3*inch
c.line(1*inch, y_pos, 7*inch, y_pos)
y_pos -= 0.3*inch

c.drawString(4*inch, y_pos, "Subtotal:")
c.drawString(5.5*inch, y_pos, "$982.94")
y_pos -= 0.25*inch

c.drawString(4*inch, y_pos, "Sales Tax (9.25%):")
c.drawString(5.5*inch, y_pos, "$90.92")
y_pos -= 0.25*inch

c.line(4*inch, y_pos, 7*inch, y_pos)
y_pos -= 0.3*inch

c.setFont("Helvetica-Bold", 12)
c.drawString(4*inch, y_pos, "TOTAL:")
c.drawString(5.5*inch, y_pos, "$1,073.86")

y_pos -= 0.5*inch
c.setFont("Helvetica", 10)
c.drawString(1*inch, y_pos, "VISA ending in 4421")
c.drawString(5.5*inch, y_pos, "$1,073.86")

# Footer
y_pos -= 1*inch
c.line(1*inch, y_pos, 7*inch, y_pos)
y_pos -= 0.3*inch
c.setFont("Helvetica", 8)
c.drawString(1*inch, y_pos, "Thank you for shopping at The Home Depot!")
c.drawString(1*inch, y_pos - 0.2*inch, "Return Policy: 90 days with receipt")
c.drawString(1*inch, y_pos - 0.4*inch, "Customer Service: 1-800-HOME-DEPOT")

# Barcode area
y_pos -= 0.8*inch
c.setFont("Courier", 10)
c.drawString(2.5*inch, y_pos, "|||| | ||| || | ||| | || |||||")
c.drawString(2.5*inch, y_pos - 0.2*inch, "8821445523018832")

c.save()
print("✅ Created 02_home_depot_receipt_washer.pdf")
PYTHON_SCRIPT