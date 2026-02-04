"""
Generate a mock pharmaceutical bid PDF for testing the Intelligence Hub.

This script creates a realistic bid document with technical specifications
that the TechnicalAgent can extract and analyze.
"""
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from datetime import datetime
import os

def create_mock_bid_pdf(filename="mock_pharmaceutical_bid.pdf"):
    """Create a mock pharmaceutical bid PDF."""
    
    # Create document
    doc = SimpleDocTemplate(filename, pagesize=letter)
    story = []
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#1a5490'),
        spaceAfter=30,
        alignment=1  # Center
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=16,
        textColor=colors.HexColor('#2c5aa0'),
        spaceAfter=12,
        spaceBefore=12
    )
    
    # Title
    story.append(Paragraph("PHARMACEUTICAL BID PROPOSAL", title_style))
    story.append(Spacer(1, 0.2*inch))
    
    # Supplier Information
    story.append(Paragraph("Supplier Information", heading_style))
    supplier_data = [
        ["Company Name:", "Acme Pharma Inc."],
        ["Address:", "123 Pharmaceutical Drive, Boston, MA 02101"],
        ["Contact Person:", "Dr. Sarah Johnson, VP of Sales"],
        ["Email:", "sarah.johnson@acmepharma.com"],
        ["Phone:", "+1 (617) 555-0123"],
        ["Date:", datetime.now().strftime("%B %d, %Y")]
    ]
    
    supplier_table = Table(supplier_data, colWidths=[2*inch, 4*inch])
    supplier_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#e8f4f8')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey)
    ]))
    story.append(supplier_table)
    story.append(Spacer(1, 0.3*inch))
    
    # Bid Summary
    story.append(Paragraph("Bid Summary", heading_style))
    story.append(Paragraph(
        "We are pleased to submit our bid for the supply of Active Pharmaceutical Ingredient (API) "
        "for your manufacturing requirements. Our proposal includes comprehensive technical specifications "
        "and competitive pricing.",
        styles['Normal']
    ))
    story.append(Spacer(1, 0.2*inch))
    
    # Technical Specifications
    story.append(Paragraph("Technical Specifications", heading_style))
    
    tech_specs_data = [
        ["Parameter", "Specification", "Unit"],
        ["Purity Level", "97.5", "%"],
        ["Yield Rate", "89.2", "%"],
        ["Storage Temperature", "2-8", "°C"],
        ["Shelf Life", "30", "months"],
        ["Particle Size", "50-100", "μm"],
        ["Moisture Content", "< 0.5", "%"],
        ["Heavy Metals", "< 10", "ppm"],
        ["Microbial Limits", "< 100", "CFU/g"]
    ]
    
    tech_table = Table(tech_specs_data, colWidths=[2.5*inch, 2*inch, 1.5*inch])
    tech_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c5aa0')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f0f0f0')])
    ]))
    story.append(tech_table)
    story.append(Spacer(1, 0.3*inch))
    
    # Quality Certifications
    story.append(Paragraph("Quality Certifications", heading_style))
    story.append(Paragraph(
        "• ISO 9001:2015 - Quality Management System<br/>"
        "• ISO 13485:2016 - Medical Devices Quality Management<br/>"
        "• GMP Certified - Good Manufacturing Practice<br/>"
        "• FDA Registered Facility<br/>"
        "• EMA Approved Supplier",
        styles['Normal']
    ))
    story.append(Spacer(1, 0.3*inch))
    
    # Pricing Information
    story.append(Paragraph("Pricing Information", heading_style))
    
    pricing_data = [
        ["Description", "Quantity", "Unit Price", "Total"],
        ["API Base Material", "1,000 kg", "$150.00/kg", "$150,000.00"],
        ["Quality Testing", "Included", "-", "$5,000.00"],
        ["Packaging & Handling", "Included", "-", "$3,000.00"],
        ["Shipping (FOB)", "Included", "-", "$2,000.00"],
        ["", "", "Total Bid Price:", "$160,000.00"]
    ]
    
    pricing_table = Table(pricing_data, colWidths=[2.5*inch, 1.5*inch, 1.5*inch, 1.5*inch])
    pricing_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c5aa0')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('GRID', (0, 0), (-1, -2), 1, colors.black),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('ROWBACKGROUNDS', (0, 1), (-1, -2), [colors.white, colors.HexColor('#f0f0f0')]),
        ('BACKGROUND', (2, -1), (-1, -1), colors.HexColor('#d4e6f1')),
        ('FONTNAME', (2, -1), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (2, -1), (-1, -1), 12),
        ('LINEABOVE', (2, -1), (-1, -1), 2, colors.black)
    ]))
    story.append(pricing_table)
    story.append(Spacer(1, 0.3*inch))
    
    # Delivery Terms
    story.append(Paragraph("Delivery Terms", heading_style))
    story.append(Paragraph(
        "• Lead Time: 45 days from purchase order<br/>"
        "• Delivery: FOB Boston, MA<br/>"
        "• Payment Terms: Net 30 days<br/>"
        "• Validity: This bid is valid for 90 days from submission date",
        styles['Normal']
    ))
    story.append(Spacer(1, 0.3*inch))
    
    # Compliance Statement
    story.append(Paragraph("Regulatory Compliance", heading_style))
    story.append(Paragraph(
        "All materials supplied will be manufactured in accordance with current Good Manufacturing "
        "Practices (cGMP) and will meet all applicable FDA, EMA, and ICH guidelines. Complete "
        "documentation including Certificate of Analysis (CoA), Certificate of Compliance (CoC), "
        "and Drug Master File (DMF) will be provided with each shipment.",
        styles['Normal']
    ))
    story.append(Spacer(1, 0.4*inch))
    
    # Signature
    story.append(Paragraph("Authorized Signature", heading_style))
    story.append(Spacer(1, 0.2*inch))
    story.append(Paragraph("_________________________________", styles['Normal']))
    story.append(Paragraph("Dr. Sarah Johnson", styles['Normal']))
    story.append(Paragraph("Vice President, Sales & Business Development", styles['Normal']))
    story.append(Paragraph("Acme Pharma Inc.", styles['Normal']))
    
    # Build PDF
    doc.build(story)
    print(f"✅ Mock bid PDF created: {filename}")
    print(f"📍 Location: {os.path.abspath(filename)}")
    return filename


if __name__ == "__main__":
    # Check if reportlab is installed
    try:
        import reportlab
    except ImportError:
        print("❌ Error: reportlab is not installed")
        print("📦 Install it with: pip install reportlab")
        exit(1)
    
    # Generate the PDF
    filename = create_mock_bid_pdf()
    
    print("\n📋 Test Data for Intelligence Hub:")
    print("   Supplier Name: Acme Pharma Inc.")
    print("   Bid Price: 160000")
    print("   Quantity: 1000")
    print("   Material Type: api_base")
    print("\n🚀 Upload this PDF to http://localhost:5137/intelligence-hub")