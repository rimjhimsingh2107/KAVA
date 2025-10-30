#!/usr/bin/env python3
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch

c = canvas.Canvas("/Users/rimjhim/Desktop/SELFPROJECTS/Kava- testing/test_realistic_claim/03_lowes_receipt_supplies.pdf", pagesize=letter)
width, height = letter

# Header
c.setFont("Helvetica-Bold", 22)
c.setFillColorRGB(0, 0.3, 0.6)
c.drawString(1*inch, height - 0.8*inch, "Lowe's")
c.setFont("Helvetica", 9)
c.setFillColorRGB(0, 0, 0)
c.drawString(1*inch, height - 1.1*inch, "Store #1342 - Campbell, CA")
c.drawString(1*inch, height - 1.3*inch, "1950 S Bascom Ave, Campbell, CA 95008")

c.line(1*inch, height - 1.5*inch, 7*inch, height - 1.5*inch)

c.setFont("Helvetica-Bold", 11)
c.drawString(1*inch, height - 1.8*inch, "CUSTOMER RECEIPT")
c.setFont("Helvetica", 9)
c.drawString(1*inch, height - 2*inch, "Date: 08/20/2025  3:47 PM")
c.drawString(1*inch, height - 2.2*inch, "Order #: 88-293847-CC")

c.line(1*inch, height - 2.4*inch, 7*inch, height - 2.4*inch)

# Items
y = height - 2.7*inch
items = [
    ("2", "Smoke Detector - First Alert 10yr Battery", "34.98"),
    ("1", "Fire Extinguisher 5lb ABC Rated", "44.99"),
    ("3", "Carbon Monoxide Detector", "89.97"),
    ("1", "Emergency Exit Light", "29.99"),
    ("4", "LED Flashlight with Batteries", "39.96"),
    ("1", "Fire Blanket - Kitchen Safety", "24.99"),
]

c.setFont("Helvetica-Bold", 9)
c.drawString(1*inch, y, "QTY")
c.drawString(1.7*inch, y, "ITEM")
c.drawString(5.5*inch, y, "TOTAL")
y -= 0.25*inch

c.setFont("Helvetica", 9)
for qty, desc, price in items:
    c.drawString(1*inch, y, qty)
    c.drawString(1.7*inch, y, desc)
    c.drawString(5.5*inch, y, f"${price}")
    y -= 0.22*inch

# Totals
y -= 0.3*inch
c.line(4*inch, y, 7*inch, y)
y -= 0.25*inch
c.drawString(4.2*inch, y, "Subtotal:")
c.drawString(5.5*inch, y, "$264.88")
y -= 0.2*inch
c.drawString(4.2*inch, y, "Tax (9.25%):")
c.drawString(5.5*inch, y, "$24.50")
y -= 0.2*inch
c.setFont("Helvetica-Bold", 11)
c.drawString(4.2*inch, y, "TOTAL:")
c.drawString(5.5*inch, y, "$289.38")

y -= 0.4*inch
c.setFont("Helvetica", 9)
c.drawString(1*inch, y, "Payment: MASTERCARD ****5567")
c.drawString(1*inch, y - 0.2*inch, "Approved: 289.38")

# Footer
y -= 1*inch
c.setFont("Helvetica", 7)
c.drawString(1.5*inch, y, "Thanks for shopping at Lowe's! Returns accepted within 90 days.")
c.drawString(2*inch, y - 0.15*inch, "Questions? Call 1-800-445-6937")

c.save()
print("✅ Created 03_lowes_receipt_supplies.pdf")
