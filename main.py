from fastapi import FastAPI
from backend.api.endpoints.company import router as company_router
from backend.api.endpoints.account import router as account_router
from backend.api.endpoints.orders import router as order_router
from backend.api.endpoints.salesman import router as salesman_router
from backend.api.endpoints.products import router as product_router

app = FastAPI(
    title="CheckMate-API", 
    description=
    "Backend for remote sales team tracking. Companies register, add their sales team and product catalogue,"
    " then send salesmen into the field. Every sale gets logged in real time with the salesman's location tagged automatically.",
    version="1.0.1"
)

app.include_router(company_router, prefix="/companies", tags=["companies"])
app.include_router(account_router, prefix="/accounts", tags=["accounts"])
app.include_router(order_router, prefix="/orders", tags=["orders"])
app.include_router(salesman_router, prefix="/salesman", tags=["salesman"])
app.include_router(product_router, prefix="/products", tags=["products"])

