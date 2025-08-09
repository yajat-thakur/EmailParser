from fastapi import FastAPI, Query, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.api.v1 import parserController
from app.models.dbController import insert_parsed_data, get_db_connection
from app.services.banks.kotakParser import parse_kotak_credit_card_from_pdf
from app.services.banks.hdfcParser import parse_hdfc_credit_card_from_pdf
from app.services.banks.iciciParser import parse_icici_credit_card_from_pdf
from app.services.banks.sbiParser import parse_sbi_credit_card_from_pdf
from app.services.banks.axisParser import parse_axis_credit_card_from_pdf
from app.services.banks.iblParser import parse_ibl_credit_card_from_pdf
from app.services.banks.yesParser import parse_yes_credit_card_from_pdf
import os
import time
import asyncio

app = FastAPI(
    title="Document Parser API",
    version="1.0.0",
    description="Parses bank/credit card statements into structured data"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(parserController.router)

BANK_PARSERS = {
    "kotak": parse_kotak_credit_card_from_pdf,
    "hdfc": parse_hdfc_credit_card_from_pdf,
    "icici": parse_icici_credit_card_from_pdf,
    "sbi": parse_sbi_credit_card_from_pdf,
    "axis": parse_axis_credit_card_from_pdf,
    "yes" : parse_yes_credit_card_from_pdf,
    "ibl" : parse_ibl_credit_card_from_pdf
}

@app.middleware("http")
async def timeout_middleware(request: Request, call_next):
    try:
        return await asyncio.wait_for(call_next(request), timeout=30.0)
    except asyncio.TimeoutError:
        return JSONResponse({"error": "Request timeout"}, status_code=504)

@app.get("/ping")
async def health_check():
    return {"message": "API is running"}

@app.get("/document-parser")
async def parse_demo_statement(
    bank: str = Query(..., description="Bank name (HDFC, ICICI, SBI, AXIS, KOTAK, YES, IBL)"),
    file_name: str = Query(..., description="File name without .pdf"),
    statement_type: str = Query(..., description="Only 'credit_card' is supported"),
    last4: str = Query(None, description="Last 4 digits of Card or GSTIN (optional)")
):
    try:
        # Validate statement type
        if statement_type.lower() != "credit_card":
            raise HTTPException(status_code=400, detail="Only 'credit_card' statement type is supported.")

        # Validate bank
        bank_lower = bank.lower()
        if bank_lower not in BANK_PARSERS:
            raise HTTPException(status_code=400, detail=f"Unsupported bank: {bank}")

        # Build file path
        file_path = f"/home/yajatrajput/Email_DocumentParser/emailReader/app/module/services/downloads/{file_name}.pdf"

        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="❌ File not found on server.")

        try:
            with open(file_path, 'rb') as f:
                if not f.readable():
                    raise HTTPException(status_code=422, detail="File exists but is unreadable.")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error reading file: {str(e)}")

        # Select parser
        parser_func = BANK_PARSERS[bank_lower]

        # Parse PDF
        start_parse = time.time()
        parsed_data = parser_func(file_path)
        parse_time = time.time() - start_parse

        if not parsed_data:
            raise HTTPException(status_code=500, detail="Parser returned empty data.")

        if not isinstance(parsed_data, dict) or not parsed_data.get("User_Details"):
            raise HTTPException(status_code=400, detail="Invalid parsed structure from parser.")

        # DB connection check
        try:
            conn = get_db_connection()
            conn.close()
        except Exception as e:
            
            raise HTTPException(status_code=503, detail=f"Database error: {e}")

        # Insert parsed data
        start_db = time.time()
        db_result = insert_parsed_data(parsed_data, bank)
        db_time = time.time() - start_db

        return {
            "status": "duplicate" if db_result.get("is_duplicate") else "success",
            "message": db_result.get("message"),
            "bank": bank,
            "statement_type": statement_type,
            "is_duplicate": db_result.get("is_duplicate", False),
            "from_cache": db_result.get("from_cache", False),
            "statement_id": db_result.get("statement_id"),
            "content_hash": db_result.get("content_hash"),
            "parsed_data": db_result.get("parsed_data", parsed_data),
            "parse_time_seconds": round(parse_time, 2),
            "db_insert_time_seconds": round(db_time, 2)
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing error: {str(e)}")
