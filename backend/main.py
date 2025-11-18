import os
from typing import List, Optional
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from database import db, create_document
from schemas import Inquiry, InquiryFile

app = FastAPI(title="Ingenieurbüro API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {"message": "Backend läuft"}


@app.get("/api/health")
def health():
    return {"status": "ok"}


class InquiryResponse(BaseModel):
    id: str
    message: str


@app.post("/api/inquiries", response_model=InquiryResponse)
async def create_inquiry(
    name: str = Form(...),
    email: str = Form(...),
    phone: str = Form(...),
    zip_city: str = Form(...),
    project_type: str = Form(...),
    description: str = Form(...),
    source: Optional[str] = Form(None),
    files: List[UploadFile] = File(default_factory=list),
):
    """Create a new inquiry with optional file uploads.
    Files are stored on disk (./uploads) and their metadata saved in DB.
    """
    # Ensure upload directory exists
    upload_dir = os.path.join(os.getcwd(), "uploads")
    os.makedirs(upload_dir, exist_ok=True)

    file_meta: List[InquiryFile] = []
    for f in files or []:
        try:
            # Create a safe file path
            safe_name = f.filename.replace("/", "_").replace("\\", "_")
            dest_path = os.path.join(upload_dir, safe_name)
            content = await f.read()
            with open(dest_path, "wb") as out:
                out.write(content)
            file_meta.append(
                InquiryFile(
                    filename=safe_name,
                    content_type=f.content_type or "application/octet-stream",
                    size=len(content),
                )
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Fehler beim Datei-Upload: {str(e)[:100]}")

    inquiry = Inquiry(
        name=name,
        email=email,
        phone=phone,
        zip_city=zip_city,
        project_type=project_type,
        description=description,
        files=file_meta,
        source=source or "website",
    )

    try:
        inserted_id = create_document("inquiry", inquiry)
        return InquiryResponse(id=inserted_id, message="Anfrage erfolgreich übermittelt")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Datenbankfehler: {str(e)[:100]}")


@app.get("/test")
def test_database():
    """Test endpoint to check if database is available and accessible"""
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }

    try:
        # Try to import database module
        from database import db as _db

        if _db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Configured"
            response["database_name"] = _db.name if hasattr(_db, 'name') else "✅ Connected"
            response["connection_status"] = "Connected"

            # Try to list collections to verify connectivity
            try:
                collections = _db.list_collection_names()
                response["collections"] = collections[:10]  # Show first 10 collections
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"

    except ImportError:
        response["database"] = "❌ Database module not found (run enable-database first)"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"

    # Check environment variables
    import os as _os
    response["database_url"] = "✅ Set" if _os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if _os.getenv("DATABASE_NAME") else "❌ Not Set"

    return response


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
