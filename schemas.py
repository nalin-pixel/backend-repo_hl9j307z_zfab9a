"""
Database Schemas

Define your MongoDB collection schemas here using Pydantic models.
These schemas are used for data validation in your application.

Each Pydantic model represents a collection in your database.
Model name is converted to lowercase for the collection name:
- User -> "user" collection
- Product -> "product" collection
- BlogPost -> "blogs" collection
"""

from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List

# Example schemas (kept for reference):

class User(BaseModel):
    name: str = Field(..., description="Full name")
    email: str = Field(..., description="Email address")
    address: str = Field(..., description="Address")
    age: Optional[int] = Field(None, ge=0, le=120, description="Age in years")
    is_active: bool = Field(True, description="Whether user is active")

class Product(BaseModel):
    title: str = Field(..., description="Product title")
    description: Optional[str] = Field(None, description="Product description")
    price: float = Field(..., ge=0, description="Price in dollars")
    category: str = Field(..., description="Product category")
    in_stock: bool = Field(True, description="Whether product is in stock")

# Application schemas
# --------------------------------------------------

class InquiryFile(BaseModel):
    filename: str
    content_type: Optional[str] = None
    size: Optional[int] = None

class Inquiry(BaseModel):
    """
    Collection name: "inquiry"
    Represents a contact/inquiry from the website with optional file uploads.
    """
    name: str = Field(..., description="Name des Anfragenden")
    email: EmailStr = Field(..., description="E-Mail-Adresse")
    phone: str = Field(..., description="Telefonnummer")
    zip_city: str = Field(..., description="Postleitzahl / Ort des Bauvorhabens")
    project_type: str = Field(..., description="Art des Vorhabens")
    description: str = Field(..., description="Kurzbeschreibung des Bauvorhabens")
    files: List[InquiryFile] = Field(default_factory=list, description="Hochgeladene Dateien (Metadaten)")
    source: Optional[str] = Field(None, description="Quelle der Anfrage, z. B. Website-Seite")
