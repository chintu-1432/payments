import os
import csv
from datetime import datetime
from flask import Flask, request, send_file, render_template
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

app = Flask(__name__)

# Create PDF receipt
def create_payment_receipt(customer_name, items, total_amount, transaction_id):
    file_name = f"receipt_{transaction_id}.pdf"
    pdf = SimpleDocTemplate(file_name, pagesize=letter)
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'title_style',
        parent=styles['Title'],
        fontSize=20,
        textColor=colors.HexColor("#2C3E50"),
        alignment=1
    )

    elements = []
    elements.append(Paragraph("<b>PAYMENT RECEIPT</b>", title_style))
    elements.append(Spacer(1, 10))
    elements.append(Paragraph(f"<b>Date:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles['Normal']))
    elements.append(Paragraph(f"<b>Transaction ID:</b> {transaction_id}", styles['Normal']))
    elements.append(Paragraph(f"<b>Customer Name:</b> {customer_name}", styles['Normal']))
    elements.append(Spacer(1, 20))

    # Items Table
    data = [["Item", "Quantity", "Unit Price (₹)", "Total (₹)"]]
    for item, qty, price in items:
        total_item_price = qty * price
        data.append([item, qty, f"{price:.2f}", f"{total_item_price:.2f}"])
    data.append(["", "", "<b>Total</b>", f"<b>{total_amount:.2f}</b>"])

    table = Table(data, colWidths=[150, 80, 100, 100])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#3498DB")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (1, 1), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('BACKGROUND', (0, 1), (-1, -1), colors.whitesmoke)
    ]))
    elements.append(table)
    elements.append(Spacer(1, 30))

    # Signature
    elements.append(Paragraph("<b>Authorized Signature</b>", styles['Normal']))
    elements.append(Spacer(1, 5))
    elements.append(Paragraph("<font name='Helvetica-Oblique' size=14 color='#2E86C1'>Chintu</font>", styles['Normal']))

    elements.append(Spacer(1, 15))
    elements.append(Paragraph("<i>Thank you for your purchase!</i>", styles['Italic']))

    pdf.build(elements)
    return file_name

# Save data to CSV
def save_to_csv(customer_name, items, total_amount, transaction_id):
    csv_file = "sales_records.csv"
    file_exists = os.path.isfile(csv_file)

    with open(csv_file, mode="a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        if not file_exists:
            writer.writerow(["Date", "Transaction ID", "Customer Name", "Item", "Quantity", "Unit Price (₹)", "Total (₹)"])

        for item, qty, price in items:
            writer.writerow([
                datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                transaction_id,
                customer_name,
                item,
                qty,
                f"{price:.2f}",
                f"{qty * price:.2f}"
            ])

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        customer_name = request.form["customer"]
        items = []
        item_names = request.form.getlist("item[]")
        quantities = request.form.getlist("qty[]")
        prices = request.form.getlist("price[]")

        for name, qty, price in zip(item_names, quantities, prices):
            if name.strip():
                items.append((name, int(qty), float(price)))

        total_amount = sum(qty * price for _, qty, price in items)
        txn_id = "TXN" + datetime.now().strftime("%Y%m%d%H%M%S")

        save_to_csv(customer_name, items, total_amount, txn_id)
        pdf_file = create_payment_receipt(customer_name, items, total_amount, txn_id)

        return send_file(pdf_file, as_attachment=True)

    return render_template("index.html")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
