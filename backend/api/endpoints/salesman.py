from backend.database.actions.salesman import (
    add_salesman, edit_salesman, delete_salesman, 
    activate_salesman, show_salesmen, search_salesmen, 
    deactivate_salesman, signin
)
from backend.database.actions.sales import generate_salesman_sales
from backend.database.actions.company import get_company_by_id
from fastapi import APIRouter, HTTPException, Depends
from backend.api.schemas.salesman import SalesmanIn, SalesmanLogin, SalesmanOut, SalesmanEdit
from fastapi.responses import FileResponse
from datetime import datetime
import csv
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, 
    Paragraph, Spacer, Image,
)
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
import os
from backend.security.jwt_handler import create_access_token
from backend.security.deps import allow_roles

router = APIRouter(prefix="/salesman")

EXPORT_DIR = "exports"
os.makedirs(EXPORT_DIR, exist_ok=True)

BASE_DIR = os.path.dirname(os.path.abspath(__file__)) 
logo_path = os.path.join(BASE_DIR, "check.png")
print("Logo path:", logo_path)
print("Exists:", os.path.exists(logo_path))

@router.get("/fetch", response_model=list[SalesmanOut], description="Show all the salesmen for your company. Requires Admin")
async def fetch_salesmen(
    sort_term: str, 
    sort_dir: str,
    user = Depends(allow_roles(["admin"]))
):
    salesmen = await show_salesmen(user.get("sub"), sort_term, sort_dir)
    if not salesmen:
        raise HTTPException(status_code=404, detail="salesmen not found")
    return salesmen

@router.get("/sales", description="Fetch all the sales by a given salesman. Requires Admin")
async def fetch_salesmen_sales(
    filter,
    salesman_id: str = "",
    user = Depends(allow_roles(["salesman", "admin"])),
):
    if user.get("role") == "admin":
        sales = await generate_salesman_sales(user.get("sub"), salesman_id, filter)
    else:
        sales = await generate_salesman_sales(user.get("company_id"), user.get("sub"), filter)
    if not sales:
        raise HTTPException(status_code=404, detail="Sales not found")
    return sales

@router.get("/search", response_model=list[SalesmanOut], description="Search a salesman by their name or contact or email. Requires Admin")
async def find_salesmen(
    search_term: str,
    user = Depends(allow_roles(["admin"]))
):
    salesmen = await search_salesmen(user.get("sub"), search_term)
    if not salesmen:
        raise HTTPException(status_code=404, detail="salesmen not found")
    return salesmen

@router.get("/export-pdf")
async def fetch_export_product_pdf(
    filter_term: str,
    user = Depends(allow_roles(["admin"]))
):
    salesmen = await show_salesmen(user.get("sub"), filter_term, "desc")
    if not salesmen:
        raise HTTPException(status_code=404, detail="Order PDF not found")

    company = await get_company_by_id(company_id)
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    
    filename = f"{company.company_name}_salesmen_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
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
    

    report_title = f"{filter_term.capitalize()} Salesmen Report"
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
            "Salesman", "Email", "Contact", "Status", 
            "Date Added"
        ]
    ]
    for s in salesmen:
        data.append([
            Paragraph(s.salesman_name or "", styles["Normal"]),
            Paragraph(s.salesman_email or "", styles["Normal"]),
            str(s.salesman_contact),
            Paragraph(s.salesman_status or "", styles["Normal"]),
            str(s.date_added)
        ])
    
    col_widths = [
        3.5*cm, 3.5*cm, 3.5*cm, 3.5*cm, 
        3.0*cm
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


@router.get("/orders-export-csv")
async def fetch_export_order_csv(
    filter_term: str,
    user = Depends(allow_roles(["admin"]))
):
    salesmen = await show_salesmen(user.get("sub"), filter_term, "desc")
    if not salesmen:
        raise HTTPException(status_code=404, detail="No orders found")

    company = await get_company_by_id(company_id)
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    filename = f"{company.company_name}_salesmen_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    path = os.path.join(EXPORT_DIR, filename)

    with open(path, mode="w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file)
        writer.writerow([
            "Salesman", "Email", "Contact", "Status",
            "Date Added"
        ])
        for s in salesmen:
            writer.writerow([
                s.salesman_name, s.salesman_email, s.salesman_contact, 
                s.salesman_status, str(s.date_added)
            ])

    return FileResponse(
        path,
        media_type="text/csv",
        filename=filename
    )

@router.post("/create", response_model=SalesmanOut)
async def create_salesman(
    detail: SalesmanIn,
    user = Depends(allow_roles(["admin"]))
):
    try:
        new_salesman = await add_salesman(detail.model_dump())
        if not new_salesman:
            raise HTTPException(status_code=400, detail="failed to add salesman")
        return new_salesman
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {e}")

@router.post("/login", response_model=SalesmanOut)
async def login_account(detail: SalesmanLogin):
    salesman_detail = {
        'name': detail.salesman_name,
        'password': detail.salesman_password
    }
    try:
        salesman = await signin(salesman_detail)
        if not salesman:
            raise HTTPException(status_code=404, detail="salesman not found")
        data = {
                "sub": str(salesman.company_id),
                "name": salesman.salesman_name,
                "email": salesman.salesman_email,
                "role": "salesman",
                "contact": salesman.salesman_contact,
                "target": salesman.salesman_target,
                "status": salesman.salesman_status
            }

        access_token = create_access_token(data)

        return {
            "access_token": access_token,
            "token_type": "Bearer"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {e}")

@router.put("/activate")
async def make_active(
    salesman_id: int,
    user = Depends(allow_roles(["admin"]))

):
    try:
        salesman = await activate_salesman(user.get("sub"), salesman_id)
        if not salesman:
            raise HTTPException(status_code=404, detail="salesman not found")
        return salesman
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {e}")

@router.put("/deactivate")
async def make_inactive(
    salesman_id: int,
    user = Depends(allow_roles(["admin"]))
):
    try:
        salesman = await deactivate_salesman(user.get("sub"), salesman_id)
        if not salesman:
            raise HTTPException(status_code=404, detail="salesman not found")
        return salesman
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {e}")

@router.put("/edit", response_model=SalesmanOut)
async def format_salesman(
    salesman_id: int, 
    detail: SalesmanEdit,
    user = Depends(allow_roles(["admin"]))
):
    try:
        salesman = await edit_salesman(user.get("sub"), salesman_id, detail.model_dump())
        if not salesman:
            raise HTTPException(status_code=404, detail="salesman not found")
        return salesman
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {e}")

@router.delete("/delete")
async def remove_salesman(
    salesman_id: int,
    user = Depends(allow_roles(["admin"]))
):
    try:
        await delete_salesman(user.get("sub"), salesman_id)
        return {"message": "salesman deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {e}")
