from backend.database.actions.orders import (
    add_order, edit_order, delete_order, 
    search_orders, show_orders, clear_order, 
    get_salesman_specific_orders, search_salesman_orders,
    date_span_orders_filter, get_order_by_id
)
from backend.database.actions.sales import generate_total_sales
from backend.database.actions.company import get_company_by_id
from backend.database.actions.products import get_product_by_order
from fastapi import APIRouter, HTTPException, Depends
from datetime import date
from backend.api.schemas.orders import OrderIn, OrderOut, OrderEdit
from fastapi.responses import FileResponse
from datetime import datetime
import csv
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, 
    Paragraph, Spacer, Image,
)
from reportlab.lib.pagesizes import A4, A5
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
import os
from backend.security.deps import allow_roles

router = APIRouter(prefix="/orders")

EXPORT_DIR = "exports"
os.makedirs(EXPORT_DIR, exist_ok=True)

BASE_DIR = os.path.dirname(os.path.abspath(__file__)) 
logo_path = os.path.join(BASE_DIR, "check.png")
print("Logo path:", logo_path)
print("Exists:", os.path.exists(logo_path))

@router.get("/fetch", response_model=list[OrderOut])
async def fetch_orders(
    filter_term: str, 
    filter_dir: str,
    user = Depends(allow_roles(["admin"]))
):
    orders = await show_orders(user.get("sub"), filter_term, filter_dir)
    if not orders:
        raise HTTPException(status_code=404, detail="orders not found")
    return orders

@router.get("/sales")
async def fetch_order_sales(
    filter: str,
    user = Depends(allow_roles(["admin"]))
):
    orders = await generate_total_sales(user.get("sub"), filter)
    if not orders:
        raise HTTPException(status_code=404, detail="Sales not found")
    return orders

@router.get("/salesman", response_model=list[OrderOut])
async def fetch_orders( 
    filter_term: str, 
    filter_dir: str,
    salesman_id: int = "",
    user = Depends(allow_roles(["salesman", "admin"]))
): 
    if user.get("role") == "admin":
        orders = await get_salesman_specific_orders(salesman_id, filter_term, filter_dir)
    else:
        orders = await get_salesman_specific_orders(user.get("sub"), filter_term, filter_dir)
    if not orders:
        raise HTTPException(status_code=404, detail="orders not found")
    return orders

@router.get("/search", response_model=list[OrderOut])
async def find_orders(
    search_by: str, 
    search_term: str,
    user = Depends(allow_roles(["admin"]))
):
    orders = await search_orders(user.get("sub"), search_by, search_term)
    if not orders:
        raise HTTPException(status_code=404, detail="orders not found")
    return orders

@router.get("/salesman-search", response_model=list[OrderOut])
async def find_orders(
    search_by: str, 
    search_term: str,
    salesman_id: int = "",
    user = Depends(allow_roles(["admin", "salesman"]))
):
    if user.get("role") == "admin":
        orders = await search_salesman_orders(salesman_id, search_by, search_term)
    else:
        orders = await search_salesman_orders(user.get("sub"), search_by, search_term)
    if not orders:
        raise HTTPException(status_code=404, detail="orders not found")
    return orders

@router.get("/date-span-filter", response_model=list[OrderOut])
async def filter_orders(
    start_date: date, 
    end_date: date,
    user = Depends(allow_roles(["admin"]))
):
    orders = await date_span_orders_filter(user.get("sub"), start_date, end_date)
    if not orders:
        raise HTTPException(status_code=404, detail="Orders not found")
    return orders

@router.get("/pdf")
async def fetch_export_orders_pdf(
    filter_term: str,
    user = Depends(allow_roles(["admin"]))
):
    orders = await show_orders(user.get("sub"), filter_term, "desc")
    if not orders:
        raise HTTPException(status_code=404, detail="Order PDF not found")

    company = await get_company_by_id(company_id)
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    
    filename = f"{company.company_name}_orders_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    path = os.path.join(EXPORT_DIR, filename)

    doc = SimpleDocTemplate(
        path, 
        pagesize=A4,
        rightMargin=30,
        leftMargin=30,
        topMargin=40,
        bottomMargin=30
    )
    
    styles = getSampleStyleSheet()
    elements = []
    

    report_title = f"{filter_term.capitalize()} Orders Report"
    custom_title = ParagraphStyle(
        'custom_title',
        parent=styles['Title'],
        alignment=1,
        fontSize=16,
        spaceAfter=10
    )
    

    if os.path.exists(logo_path):
        logo = Image(logo_path, width=80, height=80)
        logo.hAlign = 'CENTER'
        elements.append(logo)
        elements.append(Spacer(1, 6))
    

    company_info = f"""
        <b>{company.company_name}</b><br/>
        {company.company_email} | {company.company_contact}<br/>
        Date: {datetime.today().strftime("%B %d, %Y")}
    """
    elements.append(Paragraph(company_info, styles["Normal"]))
    elements.append(Spacer(1, 20))
    
    elements.append(Paragraph(report_title, custom_title))
    elements.append(Spacer(1, 12))
    

    data = [
        [
            "Order Name", "Description", "Quantity", 
            "Customer", "Email", "Contact", 
            "Status", "Date Added"
        ]
    ]
    for o in orders:
        data.append([
            Paragraph(o.order_name or "", styles["Normal"]),
            Paragraph(o.order_detail or "", styles["Normal"]),
            str(o.order_quantity),
            Paragraph(o.customer_name or "", styles["Normal"]),
            Paragraph(o.customer_email or "", styles["Normal"]),
            Paragraph(o.customer_contact or "", styles["Normal"]),
            Paragraph(o.order_status or "", styles["Normal"]),
            str(o.date_added)
        ])
    
   
    col_widths = [
        2.5*cm, 3.5*cm, 1.5*cm, 2.5*cm, 
        3.0*cm, 2.5*cm, 2.0*cm, 2.0*cm, 
        2.5*cm, 3.0*cm
    ]
    

    table = Table(data, colWidths=col_widths, repeatRows=1)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#54B108")),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('GRID', (0,0), (-1,-1), 0.4, colors.grey),
        ('BACKGROUND', (0,1), (-1,-1), colors.whitesmoke),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.whitesmoke, colors.lightgrey]),
    ]))
    
    elements.append(table)
    elements.append(Spacer(1, 20))
    

    signature = """
        <br/><br/><br/>
        ___________________________<br/>
        <b>Authorized Signature</b><br/>
        Generated by CheckMate Admin
    """
    elements.append(Paragraph(signature, styles["Normal"]))
    
    doc.build(elements)

    return FileResponse(
        path,
        media_type="application/pdf",
        filename=filename
    )

@router.get("/receipt-pdf")
async def fetch_orders_receipt(
    order_id: int,
    user = Depends(allow_roles(["admin"]))
):
    order = await get_order_by_id(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    company = await get_company_by_id(user.get("sub"))
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    product = await get_product_by_order(company_id, order.order_name)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    filename = f"{company.company_name}_receipt_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    path = os.path.join(EXPORT_DIR, filename)

    doc = SimpleDocTemplate(
        path,
        pagesize=A5, 
        rightMargin=30,
        leftMargin=30,
        topMargin=30,
        bottomMargin=30
    )

    styles = getSampleStyleSheet()
    elements = []

    logo_path = os.path.join(BASE_DIR, "static", "logo.png")
    if os.path.exists(logo_path):
        logo = Image(logo_path, width=60, height=60)
        logo.hAlign = "CENTER"
        elements.append(logo)

    company_info = f"""
        <b>{company.company_name}</b><br/>
        {company.company_email}<br/>
        {company.company_contact}
    """
    elements.append(Paragraph(company_info, styles["Title"]))
    elements.append(Spacer(1, 10))

    header_style = ParagraphStyle(
        'Header',
        parent=styles['Heading2'],
        alignment=1,
        textColor=colors.HexColor("#54B108"),
        fontSize=14,
        spaceAfter=10
    )
    elements.append(Paragraph("ORDER RECEIPT", header_style))
    elements.append(Spacer(1, 8))

    elements.append(Paragraph(f"Date: {datetime.now().strftime('%B %d, %Y')}", styles["Normal"]))
    elements.append(Spacer(1, 15))

    info_style = ParagraphStyle('Info', parent=styles['Normal'], fontSize=11, leading=14)
    order_info = f"""
        <b>Order Name:</b> {order.order_name}<br/>
        <b>Description:</b> {order.order_detail}<br/>
        <b>Quantity:</b> {order.order_quantity}<br/>
        <b>Status:</b> {order.order_status}<br/>
        <b>Customer Name:</b> {order.customer_name}<br/>
        <b>Customer Email:</b> {order.customer_email}<br/>
        <b>Customer Contact:</b> {order.customer_contact}<br/>
        <b>Date Added:</b> {order.date_added.strftime("%B %d, %Y %H:%M")}
    """
    elements.append(Paragraph(order_info, info_style))
    elements.append(Spacer(1, 20))


    total = f"{((product.product_price) * order.order_quantity):,.2f}" or "N/A"

    total_data = [
        ["", ""],
        ["TOTAL", f"KSh {total}"]
    ]
    total_table = Table(total_data, colWidths=[8 * cm, 4 * cm])
    total_table.setStyle(TableStyle([
        ('FONTNAME', (0, 1), (-1, 1), 'Helvetica-Bold'),
        ('ALIGN', (1, 1), (1, 1), 'RIGHT'),
        ('TEXTCOLOR', (0, 1), (-1, 1), colors.black),
        ('BOTTOMPADDING', (0, 1), (-1, 1), 10),
        ('TOPPADDING', (0, 1), (-1, 1), 10),
        ('LINEABOVE', (0, 1), (-1, 1), 1, colors.HexColor("#54B108")),
    ]))
    elements.append(total_table)
    elements.append(Spacer(1, 30))

    signature = """
        ___________________________<br/>
        <b>Authorized Signature</b><br/>
        <font size="8">Generated by CheckMate Admin</font>
    """
    elements.append(Paragraph(signature, styles["Normal"]))

    doc.build(elements)

    return FileResponse(
        path,
        media_type="application/pdf",
        filename=filename
    )


@router.get("/pdf")
async def fetch_export_sales_pdf(
    filter: str,
    user = Depends(allow_roles(["admin"]))
):
    sales = await generate_total_sales(user.get("sub"), filter)
    if not sales:
        raise HTTPException(status_code=404, detail="Order PDF not found")

    company = await get_company_by_id(company_id)
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    
    filename = f"{company.company_name}_last_month_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    path = os.path.join(EXPORT_DIR, filename)

    doc = SimpleDocTemplate(
        path, 
        pagesize=A4,
        rightMargin=30,
        leftMargin=30,
        topMargin=40,
        bottomMargin=30
    )
    
    styles = getSampleStyleSheet()
    elements = []
    

    report_title = f"{filter.capitalize()} sales Report"
    custom_title = ParagraphStyle(
        'custom_title',
        parent=styles['Title'],
        alignment=1,
        fontSize=16,
        spaceAfter=10
    )
    

    if os.path.exists(logo_path):
        logo = Image(logo_path, width=80, height=80)
        logo.hAlign = 'CENTER'
        elements.append(logo)
        elements.append(Spacer(1, 6))
    

    company_info = f"""
        <b>{company.company_name}</b><br/>
        {company.company_email} | {company.company_contact}<br/>
        Date: {datetime.today().strftime("%B %d, %Y")}
    """
    elements.append(Paragraph(company_info, styles["Normal"]))
    elements.append(Spacer(1, 20))
    
    elements.append(Paragraph(report_title, custom_title))
    elements.append(Spacer(1, 12))
    

    data = [
        [
            "Product Name", "Quantity", "Price", 
            "Total Sales"
        ]
    ]
    for s in sales:
        data.append([
            Paragraph(s['product_name'] or "", styles["Normal"]),
            Paragraph(str(s['quantity']) or 0, styles["Normal"]),
            Paragraph(str(s['price']) or 0.0, styles["Normal"]),
            Paragraph(str(s['total_sales']) or 0.0, styles["Normal"]),
        ])
    
   
    col_widths = [
        3.5*cm, 3.5*cm, 5.5*cm, 5.5*cm, 
    ]
    

    table = Table(data, colWidths=col_widths, repeatRows=1)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#54B108")),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('GRID', (0,0), (-1,-1), 0.4, colors.grey),
        ('BACKGROUND', (0,1), (-1,-1), colors.whitesmoke),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.whitesmoke, colors.lightgrey]),
    ]))
    
    elements.append(table)
    elements.append(Spacer(1, 20))
    

    signature = """
        <br/><br/><br/>
        ___________________________<br/>
        <b>Authorized Signature</b><br/>
        Generated by CheckMate Admin
    """
    elements.append(Paragraph(signature, styles["Normal"]))
    
    doc.build(elements)

    return FileResponse(
        path,
        media_type="application/pdf",
        filename=filename
    )


@router.get("/export-csv")
async def fetch_export_order_csv(
    filter_term: str,
    user = Depends(allow_roles(["admin"]))
):
    orders = await show_orders(user.get("sub"), filter_term, "desc")
    if not orders:
        raise HTTPException(status_code=404, detail="No orders found")

    company = await get_company_by_id(company_id)
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    filename = f"{company.company_name}_orders_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    path = os.path.join(EXPORT_DIR, filename)

    with open(path, mode="w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file)
        writer.writerow([
            "Order Name", "Description", "Quantity", 
            "Customer Name", "Customer Email", "Customer Contact",
            "Longitude", "Latitude", "Status", "Date Added"
        ])
        for o in orders:
            writer.writerow([
                o.order_name, o.order_detail, str(o.order_quantity), 
                o.customer_name, o.customer_email, o.customer_contact,
                str(o.longitude), str(o.latitude), o.order_status, str(o.date_added)
            ])

    return FileResponse(
        path,
        media_type="text/csv",
        filename=filename
    )

@router.get("/sales-export-csv")
async def fetch_export_sales_csv(
    filter: str,
    user = Depends(allow_roles(["admin"]))
):
    sales = await generate_total_sales(user.get("sub"), filter)
    if not sales:
        raise HTTPException(status_code=404, detail="No orders found")

    company = await get_company_by_id(company_id)
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    filename = f"{company.company_name}_sales_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    path = os.path.join(EXPORT_DIR, filename)

    with open(path, mode="w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file)
        writer.writerow([
            "Product Name", "Quantity", "Price", 
            "Total Sales"
        ])
        for s in sales:
            writer.writerow([
                s['product_name'], str(s['quantity']), str(s["price"]), 
                str(s['total_sales'])
            ])

    return FileResponse(
        path,
        media_type="text/csv",
        filename=filename
    )

@router.post("/create", response_model=OrderOut)
async def create_order(
    detail: OrderIn,
    user = Depends(allow_roles(["salesman", "admin"]))
):
    try:
        new_order = await add_order(detail.model_dump())
        return new_order
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {e}")

@router.put("/edit", response_model=OrderOut)
async def format_order(
    order_id: int, 
    detail: OrderEdit,
    user = Depends(allow_roles(["admin", "salesman"]))
):
    try: 
        order = await edit_order(order_id, detail.model_dump())
        if not order: 
            raise HTTPException(status_code=404, detail="order not found")
        return order
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {e}")

@router.put("/clear", response_model=OrderOut)
async def check_order(
    order_id: int,
    user = Depends(allow_roles(["admin", "salesman"]))
):
    try:
        order = await clear_order(order_id)
        if not order:
            raise HTTPException(status_code=404, detail="order not found")
        return order
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {e}")

@router.delete("/delete")
async def remove_order(
    order_id: int,
    user = Depends(allow_roles(["admin", "salesman"]))
):
    try:
        await delete_order(order_id)
        return {"message": "order deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {e}")
