from backend.database.actions.company import add_company, edit_company, show_companies, search_companies, delete_company, signin
from fastapi import APIRouter, HTTPException, Depends
from backend.api.schemas.company import CompanyIn, CompanyOut, CompanyLogin
from backend.security.deps import allow_roles
from backend.security.jwt_handler import create_access_token

router = APIRouter(prefix="/company")

@router.get("/fetch", response_model=list[CompanyOut])
async def fetch_companies(
    sort_dir: str, 
    sort_term: str = "all",
    user = Depends(allow_roles(["superadmin"]))
):
    companies = await show_companies(sort_term, sort_dir)
    if not companies:
        raise HTTPException(status_code=404, detail="Companies not found")
    return companies

@router.get("/companies-search/", response_model=list[CompanyOut])
async def find_companies(
    search_term: str,
    user = Depends(allow_roles(["superadmin"]))
):
    companies = await search_companies(search_term)
    if not companies:
        raise HTTPException(status_code=404, detail="Company not found")
    return companies

@router.post("/companies-create/", response_model = CompanyOut)
async def register_companies(company: CompanyIn):
    try:
        new_company = await add_company(company_detail=company.model_dump())
        return new_company
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {e}")

@router.post("/companies-login/", response_model=CompanyOut)
async def login(credential: CompanyLogin):
    details = {
            "name": credential.company_name,
            "password": credential.company_password
        }
    try:
        company = await signin(company_detail=details)
        if not company:
            raise HTTPException(status_code=404, detail="company not found")
        data = {
            "sub": str(company.company_id),
            "name": company.company_name,
            "email": company.company_email,
            "role": "admin",
            "contact": company.company_contact
        }

        access_token = create_access_token(data)

        return {
            "access_token": access_token,
            "token_type": "Bearer"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {e}")
            

@router.put("/companies-edit/", response_model=CompanyOut)
async def format_company(
    detail: CompanyIn,
    user = Depends(allow_roles(["admin"]))
):
    try:
        company = await edit_company(user.get("sub"), detail.model_dump())
        if not company:
            raise HTTPException(status_code=404, detail="company not found")
        return company
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {e}")

@router.delete("/companies-delete/")
async def remove_company(
    user = Depends(allow_roles(["admin"]))
):
    try:
        await delete_company(user.get("sub"))
        return {"message": "company deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {e}")
