from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime
from pydantic import field_validator
import re


class Product(SQLModel, table=True):

    id: Optional[int] = Field(
        default=None,
        primary_key=True
    )

    name: str = Field(index=True)
    description: str
    brand: str = Field(index=True)
    category: str = Field(index=True)

    price: float = Field(gt=0)
    stock: int = Field(ge=0)

    warranty_months: int = Field(ge=0)

    sku: str = Field(
        unique=True,
        index=True
    )

    supplier_id: Optional[int] = Field(
        default=None,
        foreign_key="supplier.id"
    )

    created_at: datetime = Field(
        default_factory=datetime.utcnow
    )

    updated_at: datetime = Field(
        default_factory=datetime.utcnow
    )



class ProductCreate(SQLModel):

    name: str = Field(
        min_length=2,
        max_length=100
    )

    description: str = Field(
        min_length=10,
        max_length=500
    )

    brand: str
    category: str

    price: float
    stock: int

    warranty_months: int

    sku: str

    supplier_id: Optional[int] = None



    @field_validator("name")
    def validate_name(cls, v):

        if not v[0].isupper():
            raise ValueError(
                "Name must start with a capital letter"
            )

        if re.search(
            r"[^a-zA-Z0-9\s-]",
            v
        ):
            raise ValueError(
                "Name cannot contain special characters"
            )

        return v



    @field_validator("brand")
    def validate_brand(cls, v):

        allowed = [
            "HP",
            "Dell",
            "Lenovo",
            "Apple",
            "Samsung",
            "Intel",
            "AMD",
            "Corsair",
            "Logitech",
            "Other"
        ]

        for brand in allowed:

            if v.lower() == brand.lower():
                return brand

        raise ValueError(
            "Invalid brand"
        )



    @field_validator("category")
    def validate_category(cls, v):

        allowed = [
            "Laptops",
            "Monitors",
            "Storage",
            "Processors",
            "Memory",
            "Keyboards",
            "Mice",
            "Accessories"
        ]

        for category in allowed:

            if v.lower() == category.lower():
                return category

        raise ValueError(
            "Invalid category"
        )



    @field_validator("price")
    def validate_price(cls, v):

        if v < 100:
            raise ValueError(
                "Price must be at least 100 KSh"
            )

        if v > 500000:
            raise ValueError(
                "Price cannot exceed 500000 KSh"
            )

        return round(v, 2)



    @field_validator("sku")
    def validate_sku(cls, v):

        pattern = r"^[A-Z]{3,4}-[A-Z]{2,4}-[0-9]{4}$"

        if not re.match(pattern, v):
            raise ValueError(
                "SKU must follow format CAT-BRAND-XXXX"
            )

        return v



    @field_validator("warranty_months")
    def validate_warranty(cls, v):

        if v > 36:

            raise ValueError(
                "Warranty cannot exceed 36 months"
            )

        return v





# Exercise 4 model

class StockAdjustment(SQLModel):

    product_id: int

    quantity_to_add: int = Field(
        gt=0
    )