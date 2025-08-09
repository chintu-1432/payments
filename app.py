import os
import csv
from flask import Flask, request, send_file
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from datetime import datetime

app = Flask(__name__)

# Route for HTML form
@app.route('/')
def home():
    return send_file("index.html")

# Route for generating receipt
@app.route('/generate', methods=['POST'])
def generate_receipt():
    customer = request.form['customer']
    items = request.form.getlist('item[]')
    quantities = request.form.getlist('quantity[]')
    prices = request.form.getlist('price[]')

    purchased_items = []
    for item, qty, price in zip(items, quantities, prices):
        purchased_items.append((item, int(qty), float(price)))

    # Store data in CSV
    csv_file = "sales_records.csv"
    file_exists = os.path.isfile(csv_file)
    with open(csv_file, mode="a", newline="") as file:
        writer = csv.writer(file)
        if not file_exists:
            writer.writerow(["Date", "Customer", "Item", "Quantity", "Price"])
        for item, qty, price in purchased_items:
            writer.writerow([datetime.now().strftime("%Y-%m-%d %H:%M:%S"), customer, item, qty, price])

    # Generate PDF receipt
    filename = f"receipt_{datetime.now().strftime('%Y%m%d%H%M%S')}.pdf"
    doc = SimpleDocTemplate(filename, pagesize=A4)
    styles = getSampleStyleSheet()
    elements = []

    elements.append(Paragraph("<b>PAYMENT RECEIPT</b>", styles['Title']))
    elements.append(Spacer(1, 12))
    elements.append(Paragraph(f"<b>Customer Name:</b> {customer}", styles['Normal']))
    elements.append(Paragraph(f"<b>Date:</b> {datetime.now().strftime('%d-%m-%Y %H:%M:%S')}", styles['Normal']))
    elements.append(Spacer(1, 12))

    data = [["Item", "Quantity", "Price (₹)", "Total (₹)"]]
    total_amount = 0
    for item, qty, price in purchased_items:
        total = qty * price
        total_amount += total
        data.append([item, qty, f"{price:.2f}", f"{total:.2f}"])

    data.append(["", "", "<b>Total</b>", f"<b>{total_amount:.2f}</b>"])
    table = Table(data, colWidths=[200, 80, 100, 100])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    elements.append(table)
    elements.append(Spacer(1, 24))

    elements.append(Paragraph("Signature: Chintu", styles['Normal']))

    doc.build(elements)

    return send_file(filename, as_attachment=True)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

