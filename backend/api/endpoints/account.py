from backend.database.actions.account import delete_account, create_account, edit_account, show_accounts, search_accounts, signin
from fastapi import APIRouter, HTTPException, Depends, Header
from backend.api.schemas.account import AccountIn, AccountLogin, AccountOut, AccountEdit
from backend.security.jwt_handler import create_access_token
from backend.security.deps import allow_roles


router = APIRouter(prefix="/account")


@router.get("/fetch", response_model=list[AccountOut], description="Fetches all the accounts")
async def fetch_accounts(
    sort_term: str, 
    sort_dir: str,
    user = Depends(allow_roles(["account", "admin",]))
):
    accounts = await show_accounts(user.get("company_id"), sort_term, sort_dir)
    if not accounts:
        raise HTTPException(status_code=404, detail="Accounts not found")
    return accounts

@router.get("/search", response_model=list[AccountOut], description="Search for accounts by kew word")
async def find_accounts(
    search_term: str,
    user = Depends(allow_roles(roles=["account", "admin"]))
):
    accounts = await search_accounts(user.get("company_id"), search_term)
    if not accounts:
        raise HTTPException(status_code=404, detail="Accounts not found")
    return accounts

@router.post("/create", response_model=AccountOut, description="Create a new account")
async def add_account(account: AccountIn):
    try:
        new_account = await create_account(account_detail=account.model_dump())
        if not account:
            raise HTTPException(status_code=400, detail = "Failed to create account")
        return new_account
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occureed: {e}")

@router.post("/login", description="Generate the access token")
async def signin_to_account(detail: AccountLogin):
    account_detail = {
        'name': detail.account_name,
        'password': detail.account_password
    }
    try:
        account = await signin(account_detail)
        if not account:
            raise HTTPException(status_code=404, detail="account not found")
        data = {
            "sub": str(account.account_id),
            "company_id": account.company_id,
            "role": "account",
            "email": account.account_email,
            "contact": account.account_contact
        }

        access_token = create_access_token(
            data=data,
        )
        return {
            "access_token": access_token,
            "token_type": "Bearer"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {e}")


@router.put("/edit", description="Edit an account ")
async def format_account(
    detail: AccountEdit,
    user = Depends(allow_roles(["account", "admin"]))
):

    try:
        account = await edit_account(user.get("sub"), detail.model_dump())
        if not account:
            raise HTTPException(status_code=404, detail="account not found")
        return account
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {e}")

@router.delete("/delete", description="Remove an account from the database. This is permanent btw")
async def remove_account(user = Depends(allow_roles(["account"]))):
    try:
        await delete_account(account_id)
        return {"message": "account deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Acn error occurred: {e}")
