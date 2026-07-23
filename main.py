from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.responses import JSONResponse

from sqlmodel import SQLModel, Session, select

from typing import List
from datetime import datetime


from database.session import engine, get_session

from models.product import (
    Product,
    ProductCreate,
    StockAdjustment
)

from models.supplier import (
    Supplier,
    SupplierCreate
)



app = FastAPI(
    title="TechVault API",
    version="1.0.0"
)



# Create tables

@app.on_event("startup")
def startup():

    SQLModel.metadata.create_all(
        engine
    )



# =========================
# ERROR HANDLER
# =========================


@app.exception_handler(HTTPException)
async def http_exception_handler(
    request: Request,
    exc: HTTPException
):

    return JSONResponse(

        status_code=exc.status_code,

        content={

            "success": False,

            "status_code": exc.status_code,

            "message": exc.detail,

            "errors": [],

            "timestamp": datetime.utcnow().isoformat(),

            "path": request.url.path
        }
    )





# =========================
# PRODUCTS
# =========================



@app.post(
    "/products",
    response_model=Product
)
def create_product(
    product: ProductCreate,
    session: Session = Depends(get_session)
):


    if product.supplier_id:

        supplier = session.get(
            Supplier,
            product.supplier_id
        )


        if not supplier:

            raise HTTPException(
                404,
                "Supplier not found"
            )



    existing = session.exec(

        select(Product)
        .where(
            Product.sku == product.sku
        )

    ).first()



    if existing:

        raise HTTPException(
            400,
            "SKU already exists"
        )



    db_product = Product(
        **product.dict()
    )


    session.add(db_product)

    session.commit()

    session.refresh(db_product)


    return db_product





@app.get(
    "/products",
    response_model=List[Product]
)
def get_products(
    session: Session = Depends(get_session)
):

    return session.exec(
        select(Product)
    ).all()





# =========================
# BULK PRICE UPDATE
# =========================


@app.patch(
    "/products/bulk-update"
)
def bulk_update_price(

    category: str,

    discount_percent: float,

    session: Session = Depends(get_session)

):


    if discount_percent < 0 or discount_percent > 100:

        raise HTTPException(
            400,
            "Discount must be between 0 and 100"
        )



    products = session.exec(

        select(Product)
        .where(
            Product.category == category
        )

    ).all()



    if not products:

        raise HTTPException(
            404,
            "No products found in this category"
        )



    updated = 0



    for product in products:


        new_price = product.price * (
            1 - discount_percent / 100
        )



        if new_price < 100:

            raise HTTPException(
                400,
                "New price cannot be below 100 KSh"
            )


        product.price = round(
            new_price,
            2
        )


        product.updated_at = datetime.utcnow()


        updated += 1



    session.commit()



    return {

        "message": "Bulk update successful",

        "category": category,

        "discount": discount_percent,

        "products_updated": updated

    }





# =========================
# STOCK ADJUSTMENT
# =========================


@app.patch(
    "/products/adjust-stock"
)
def adjust_stock(

    adjustments: List[StockAdjustment],

    session: Session = Depends(get_session)

):


    successful = []

    failed = []



    for item in adjustments:


        product = session.get(
            Product,
            item.product_id
        )


        if not product:

            failed.append({

                "product_id": item.product_id,

                "reason": "Product not found"

            })

            continue



        new_stock = (
            product.stock
            +
            item.quantity_to_add
        )



        if new_stock > 5000:

            failed.append({

                "product_id": item.product_id,

                "reason": "Stock cannot exceed 5000"

            })

            continue



        product.stock = new_stock

        product.updated_at = datetime.utcnow()



        successful.append({

            "product_id": product.id,

            "new_stock": product.stock

        })



    session.commit()



    return {

        "message": "Stock adjustment completed",

        "successful_updates": successful,

        "failed_updates": failed

    }