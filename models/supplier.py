from sqlmodel import SQLModel, Field
from typing import Optional
from pydantic import field_validator
import re


class Supplier(SQLModel, table=True):

    id: Optional[int] = Field(
        default=None,
        primary_key=True
    )

    name: str = Field(
        unique=True,
        index=True
    )

    contact_person: str

    email: str = Field(
        unique=True,
        index=True
    )

    phone: str

    is_active: bool = Field(
        default=True
    )


class SupplierCreate(SQLModel):

    name: str = Field(
        min_length=2,
        max_length=100
    )

    contact_person: str = Field(
        min_length=2,
        max_length=100
    )

    email: str

    phone: str

    is_active: bool = True


    @field_validator("email")
    def validate_email(cls, v):

        pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"

        if not re.match(pattern, v):
            raise ValueError(
                "Invalid email format"
            )

        return v


    @field_validator("phone")
    def validate_phone(cls, v):

        pattern = r"^(\+254|0)[0-9]{9}$"

        if not re.match(pattern, v):
            raise ValueError(
                "Phone must be a valid Kenyan phone number"
            )

        return v