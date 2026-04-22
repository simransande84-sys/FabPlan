# core/services/reports.py
from io import BytesIO
import openpyxl
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_RIGHT, TA_LEFT
from datetime import datetime, timedelta
from core.models import Order, DesignItem, CutPiece, Profile
from .hardware_engine import calculate_hardware
from .glass_engine import calculate_glass
from .bar_optimizer import optimize_profile_cuts

def generate_quotation_pdf():
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    p.setFont("Helvetica-Bold", 16)
    p.drawString(100, 750, "Detailed Quotation")
    
    orders = Order.objects.all()
    
    y = 700
    grand_total = 0
    
    for order in orders:
        if y < 200:
            p.showPage()
            y = 750
            
        p.setFont("Helvetica-Bold", 12)
        p.drawString(100, y, f"Order {order.code} - {order.customer_name or 'No Name'}")
        y -= 20
        
        order_total = 0
        
        for design in order.designs.all():
            p.setFont("Helvetica-Bold", 10)
            p.drawString(110, y, f"Item: {design.get_product_type_display()} ({design.get_typology_display()}) - {design.width}x{design.height} - Qty: {design.quantity}")
            y -= 15
            
            p.setFont("Helvetica", 10)
            
            profile_cost = 0
            cuts = design.cut_pieces.all()
            for cut in cuts:
                cost_per_mm = cut.profile.cost_per_bar / cut.profile.bar_length
                profile_cost += (cost_per_mm * cut.length * cut.quantity)
                
            hw_cost = 0
            hw_list = calculate_hardware(design)
            for hw in hw_list:
                hw_cost += hw['quantity'] * 50
                
            glass_cost = 0
            glass_list = calculate_glass(design)
            for g in glass_list:
                area_sqm = (g['width'] / 1000) * (g['height'] / 1000)
                glass_cost += area_sqm * g['quantity'] * 100
                
            labor_cost = 200 * design.quantity
            
            total_design_cost = profile_cost + hw_cost + glass_cost + labor_cost
            order_total += total_design_cost
            
            p.drawString(120, y, f"- Profile Material: ${profile_cost:.2f}")
            y -= 15
            p.drawString(120, y, f"- Hardware: ${hw_cost:.2f}")
            y -= 15
            p.drawString(120, y, f"- Glass: ${glass_cost:.2f}")
            y -= 15
            p.drawString(120, y, f"- Labor: ${labor_cost:.2f}")
            y -= 20
            
        p.setFont("Helvetica-Bold", 10)
        p.drawString(120, y, f"Total for Order {order.code}: ${order_total:.2f}")
        y -= 30
        grand_total += order_total

    if y < 100:
        p.showPage()
        y = 750
        
    y -= 20
    p.setFont("Helvetica-Bold", 14)
    p.drawString(100, y, f"Grand Total: ${grand_total:.2f}")

    p.showPage()
    p.save()
    buffer.seek(0)
    return buffer

def generate_quotation_excel():
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Detailed Quotation"
    
    ws.append(["Order Code", "Product", "Typology", "Dimensions", "Quantity", "Profile Cost", "Hardware Cost", "Glass Cost", "Labor Cost", "Total Cost"])
    
    orders = Order.objects.all()
    grand_total = 0
    
    for order in orders:
        for design in order.designs.all():
            profile_cost = sum((cut.profile.cost_per_bar / cut.profile.bar_length) * cut.length * cut.quantity for cut in design.cut_pieces.all())
            
            hw_cost = sum(hw['quantity'] * 50 for hw in calculate_hardware(design))
            
            glass_cost = sum(((g['width'] / 1000) * (g['height'] / 1000)) * g['quantity'] * 100 for g in calculate_glass(design))
            
            labor_cost = 200 * design.quantity
            total_design_cost = profile_cost + hw_cost + glass_cost + labor_cost
            grand_total += total_design_cost
            
            ws.append([
                order.code, design.get_product_type_display(), design.get_typology_display(), f"{design.width}x{design.height}", 
                design.quantity, round(profile_cost, 2), round(hw_cost, 2), 
                round(glass_cost, 2), round(labor_cost, 2), round(total_design_cost, 2)
            ])
        
    ws.append(["", "", "", "", "", "", "", "", "Grand Total", round(grand_total, 2)])
    
    buffer = BytesIO()
    wb.save(buffer)
    buffer.seek(0)
    return buffer

def generate_material_boq_pdf():
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    p.setFont("Helvetica-Bold", 16)
    p.drawString(100, 750, "Material BOQ")
    
    y = 700
    p.setFont("Helvetica", 12)
    
    orders = Order.objects.all()
    for order in orders:
        p.setFont("Helvetica-Bold", 12)
        p.drawString(100, y, f"Order: {order.code}")
        y -= 20
        p.setFont("Helvetica", 10)
        
        for design in order.designs.all():
            p.drawString(110, y, f"Design: {design.get_typology_display()} ({design.width}x{design.height})")
            y -= 15
            # Hardware
            hw_list = calculate_hardware(design)
            for hw in hw_list:
                p.drawString(120, y, f"Hardware: {hw['name']} (Qty: {hw['quantity']})")
                y -= 15
                
            # Glass
            glass_list = calculate_glass(design)
            for g in glass_list:
                p.drawString(120, y, f"Glass Pane: {g['width']}x{g['height']} (Qty: {g['quantity']})")
                y -= 15
                
        y -= 10
        if y < 100:
            p.showPage()
            y = 750
            p.setFont("Helvetica", 10)
            
    p.showPage()
    p.save()
    buffer.seek(0)
    return buffer

def generate_cutting_chart_pdf():
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    p.setFont("Helvetica-Bold", 16)
    p.drawString(100, 750, "Bar Cutting Chart & Optimization")
    
    y = 700
    
    all_cuts = CutPiece.objects.all()
    optimized = optimize_profile_cuts(all_cuts)
    
    for profile_name, bars in optimized.items():
        p.setFont("Helvetica-Bold", 14)
        p.drawString(100, y, f"Profile: {profile_name}")
        y -= 20
        
        p.setFont("Helvetica", 10)
        for i, bar in enumerate(bars):
            p.drawString(120, y, f"Bar {i+1}: Cuts: {bar['cuts']} | Leftover: {bar['leftover']}mm | Waste: {bar['waste_percentage']}%")
            y -= 15
            
            if y < 100:
                p.showPage()
                y = 750
                p.setFont("Helvetica", 10)
                
        y -= 10

    p.showPage()
    p.save()
    buffer.seek(0)
    return buffer

def generate_single_quotation_pdf(order_id):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
    elements = []
    
    try:
        order = Order.objects.get(id=order_id)
    except Order.DoesNotExist:
        return None
        
    styles = getSampleStyleSheet()
    
    # Header Table
    header_data = [
        [Paragraph("<b>INVOICE</b>", ParagraphStyle(name='Header1', fontSize=24, textColor=colors.black)), 
         Paragraph("<font size=18 color='#2563eb'><b>FabPlan</b></font><br/>Fabrication Software", ParagraphStyle(name='Header2', alignment=TA_RIGHT))]
    ]
    header_table = Table(header_data, colWidths=[3*inch, 4.5*inch])
    header_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (0, 0), 'LEFT'),
        ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 20),
    ]))
    elements.append(header_table)
    
    # Address Line
    elements.append(Paragraph("<font size=8 color='gray'>FabPlan, 123 Tech Lane, Innovation City, 90210, United States</font>", styles['Normal']))
    elements.append(Spacer(1, 30))
    
    # Bill To & Dates Table
    issue_date = datetime.now().strftime("%d/%m/%Y")
    due_date = (datetime.now() + timedelta(days=14)).strftime("%d/%m/%Y")
    
    bill_to_data = [
        [Paragraph("<b>BILL TO</b><br/>Your client<br/>11 Beech Dr<br/>Ellington<br/>NE61 5EU<br/>United Kingdom", styles['Normal']), 
         Paragraph("Invoice No.:<br/>Issue date:<br/>Due date:", ParagraphStyle(name='labels', alignment=TA_RIGHT, fontSize=10)),
         Paragraph(f"<b>INV-{order.code}</b><br/><b>{issue_date}</b><br/><b>{due_date}</b>", ParagraphStyle(name='vals', alignment=TA_RIGHT, fontSize=10))]
    ]
    bill_table = Table(bill_to_data, colWidths=[4*inch, 1.5*inch, 2*inch])
    bill_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('ALIGN', (1, 0), (2, 0), 'RIGHT'),
    ]))
    elements.append(bill_table)
    elements.append(Spacer(1, 30))
    
    # Calculations aggregated over all designs in the order
    profile_cost = 0
    hw_cost = 0
    glass_cost = 0
    labor_cost = 0
    
    for design in order.designs.all():
        profile_cost += sum((c.profile.cost_per_bar / c.profile.bar_length) * c.length * c.quantity for c in design.cut_pieces.all())
        hw_cost += sum(hw['quantity'] * 50 for hw in calculate_hardware(design))
        glass_cost += sum(((g['width'] / 1000) * (g['height'] / 1000)) * g['quantity'] * 100 for g in calculate_glass(design))
        labor_cost += 200 * design.quantity
        
    total_qty = sum(d.quantity for d in order.designs.all())
    
    # Items Table
    table_data = [
        ['DESCRIPTION', 'QUANTITY', 'UNIT PRICE ($)', 'AMOUNT ($)'],
        [f"Profile Material (Multiple)", f"{total_qty} units", f"{profile_cost/max(total_qty, 1):.2f}", f"{profile_cost:.2f}"],
        ["Hardware & Accessories", f"{total_qty} units", f"{hw_cost/max(total_qty, 1):.2f}", f"{hw_cost:.2f}"],
        ["Glass Panels", f"{total_qty} units", f"{glass_cost/max(total_qty, 1):.2f}", f"{glass_cost:.2f}"],
        ["Cutting & Labor", f"{total_qty} units", "200.00", f"{labor_cost:.2f}"]
    ]
    
    items_table = Table(table_data, colWidths=[3.5*inch, 1.5*inch, 1.25*inch, 1.25*inch])
    items_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#f3f4f6")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 9),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
        ('TOPPADDING', (0, 0), (-1, 0), 10),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#e5e7eb")),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('PADDING', (0, 1), (-1, -1), 10),
    ]))
    elements.append(items_table)
    
    # Totals Table
    subtotal = profile_cost + hw_cost + glass_cost + labor_cost
    vat = subtotal * 0.20
    total = subtotal + vat
    
    totals_data = [
        ["SUBTOTAL:", f"${subtotal:.2f}"],
        [f"VAT 20% from ${subtotal:.2f}", f"${vat:.2f}"],
        ["TOTAL (USD):", f"${total:.2f}"],
        ["TOTAL DUE (USD):", f"${total:.2f}"]
    ]
    
    totals_table = Table(totals_data, colWidths=[2.5*inch, 1.25*inch])
    totals_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
        ('PADDING', (0, 0), (-1, -1), 10),
        ('LINEABOVE', (0, 0), (-1, 0), 0.5, colors.HexColor("#e5e7eb")),
        ('BACKGROUND', (0, 3), (1, 3), colors.HexColor("#60a5fa")),
        ('TEXTCOLOR', (0, 3), (1, 3), colors.white),
        ('FONTNAME', (0, 3), (1, 3), 'Helvetica-Bold'),
    ]))
    
    wrapper_data = [['', totals_table]]
    wrapper_table = Table(wrapper_data, colWidths=[3.75*inch, 3.75*inch])
    wrapper_table.setStyle(TableStyle([
        ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
        ('VALIGN', (1, 0), (1, 0), 'TOP'),
        ('LEFTPADDING', (0,0), (-1,-1), 0),
        ('RIGHTPADDING', (0,0), (-1,-1), 0)
    ]))
    elements.append(wrapper_table)
    
    # Footer
    elements.append(Spacer(1, 100))
    elements.append(Paragraph("<font size=8><b>FabPlan</b>, 123 Tech Lane, Innovation City, 90210, United States Email: billing@fabplan.com</font>", ParagraphStyle(name='footer', alignment=TA_LEFT)))
    
    doc.build(elements)
    buffer.seek(0)
    return buffer
