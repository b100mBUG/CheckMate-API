from backend.database.actions.account import delete_account, create_account, edit_account, show_accounts, search_accounts, signin
from fastapi import APIRouter, HTTPException
from backend.api.schemas.account import AccountIn, AccountLogin, AccountOut, AccountEdit
from backend.security import jwt_handler

router = APIRouter()

@router.get("/accounts-fetch/", response_model=list[AccountOut])
async def fetch_accounts(company_id: int, sort_term: str, sort_dir: str):
    accounts = await show_accounts(company_id, sort_term, sort_dir)
    if not accounts:
        raise HTTPException(status_code=404, detail="Accounts not found")
    return accounts

@router.get("/accounts-search/", response_model=list[AccountOut])
async def find_accounts(company_id: int, search_term: str):
    accounts = await search_accounts(company_id, search_term)
    if not accounts:
        raise HTTPException(status_code=404, detail="Accounts not found")
    return accounts

@router.post("/accounts-create/", response_model=AccountOut)
async def add_account(account: AccountIn):
    try:
        new_account = await create_account(account_detail=account.model_dump())
        if not account:
            raise HTTPException(status_code=400, detail = "Failed to create account")
        return new_account
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occureed: {e}")

@router.post("/accounts-login", response_model=AccountOut)
async def signin_to_account(detail: AccountLogin):
    account_detail = {
        'name': detail.account_name,
        'password': detail.account_password
    }
    try:
        account = await signin(account_detail)
        if not account:
            raise HTTPException(status_code=404, detail="account not found")
        return account
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {e}")

@router.put("/accounts-edit/")
async def format_account(account_id: int, detail: AccountEdit):
    try:
        account = await edit_account(account_id, detail.model_dump())
        if not account:
            raise HTTPException(status_code=404, detail="account not found")
        return account
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {e}")

@router.delete("/accounts-delete/")
async def remove_account(account_id: int):
    try:
        await delete_account(account_id)
        return {"message": "account deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Acn error occurred: {e}")
