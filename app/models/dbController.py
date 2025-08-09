import uuid
import json
import hashlib
import mysql.connector
from mysql.connector import Error
from app.core.config import settings
from typing import Dict, Optional, List, Any
from datetime import datetime
from dateutil.parser import parse


def get_db_connection():
    return mysql.connector.connect(
        host=settings.DB_HOST,
        user=settings.DB_USER,
        password=settings.DB_PASSWORD,
        database=settings.DB_NAME,
        pool_size=5,
        autocommit=False
    )


def safe_extract(data: Dict[str, Any], keys: List[str], default: Any = None) -> Any:
    for key in keys:
        if key in data:
            return data[key]
    return default


def normalize_date_flexible(raw_date: str) -> Optional[str]:
    if not raw_date:
        return None
    try:
        dt = parse(raw_date.strip(), dayfirst=True)
        return dt.strftime("%Y-%m-%d")
    except Exception:
        return None


def generate_content_hash(data: Dict) -> str:
    normalized = json.dumps(data, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def insert_parsed_data(parsed_data: Dict, bank: str, user_id: Optional[str] = None) -> Dict:
    conn = cursor = None
    result = {
        "success": False,
        "message": "",
        "inserted_rows": 0,
        "statement_id": None,
        "is_duplicate": False,
        "content_hash": None
    }

    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        conn.start_transaction()

        user_details = parsed_data.get("User_Details", {})
        account_summary = parsed_data.get("Account_summary", parsed_data.get("Account_Summary", {}))
        transactions = parsed_data.get("transactions", parsed_data.get("Transactions", []))

        content_hash = generate_content_hash(parsed_data)
        result["content_hash"] = content_hash

        card_number = (
            safe_extract(account_summary, ["Primary CardNumber", "Card_number", "Card Number"]) or
            safe_extract(account_summary, ["Card_number", "Card Number"])
        )
        card_number = str(card_number).replace(" ", "")[:20] if card_number else None

        stmt_date = (
            safe_extract(account_summary, ["Statement_date", "Statement Date", "StatementDate"]) or
            safe_extract(account_summary, ["Statement_date", "Statement Date"])
        )
        stmt_date = normalize_date_flexible(stmt_date)

        cursor.execute("""
            SELECT id, content_hash FROM userDocumentParser 
            WHERE (Card_number = %s AND Statement_date = %s)
               OR content_hash = %s
            LIMIT 1 FOR UPDATE
        """, (card_number, stmt_date, content_hash))

        existing = cursor.fetchone()
        if existing:
            result.update({
                "message": "Duplicate statement found (metadata or content hash match)",
                "statement_id": existing['id'].hex(),
                "is_duplicate": True,
                "matched_existing_hash": existing.get('content_hash'),
                "parsed_data": parsed_data,
                "from_cache": True
            })
            conn.commit()
            return result

        stmt_id = uuid.uuid4().bytes
        created_at = datetime.utcnow()

        stmt_values = (
            stmt_id,
            bank.upper(),
            # json.dumps(user_details, ensure_ascii=False),
            safe_extract(user_details,["Credit_card"]),
            safe_extract(user_details, ["Name", "Customer Name", "Holder Name"]),
            safe_extract(user_details, ["Email", "Email ID", "Email Address"]),
            safe_extract(user_details, ["Address", "Customer Address", "Billing Address"]),
            safe_extract(user_details, ["GSTIN", "GST_No", "GST Number"]),
            card_number,
            stmt_date,
            safe_extract(account_summary, ["Remember to PayBy", "Payment Due Date", "Due Date"]),
            safe_extract(account_summary, ["Total_payment_due", "Total Amount Due", "Total Due"]),
            safe_extract(account_summary, ["Credit_limit", "Credit Limit"]),
            safe_extract(account_summary, ["Available_credit_limit", "Available Credit Limit"]),
            safe_extract(account_summary, ["Available_cash_limit", "Available Cash Limit"]),
            json.dumps({
                "rewards": parsed_data.get("Rewards", {})
            }, ensure_ascii=False),
            user_id,
            content_hash,
            created_at,
            created_at.year
        )

        cursor.execute("""
            INSERT INTO userDocumentParser (
                id, bank, Credit_card, Name, Email, Address, GST_No,
                Card_number, Statement_date, Payment_due_date,
                Total_payment_dues, Credit_limit, Available_credit_limit,
                Available_cash_limit, Meta_Data, user_id,
                content_hash, created_at, archive_year
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE id=id
        """, stmt_values)
        result["inserted_rows"] = 1

        # Insert transactions
        if transactions:
            tx_values = []
            for tx in transactions:
                if not isinstance(tx, dict):
                    continue
                tx_id = uuid.uuid4().bytes
                tx_date = normalize_date_flexible(str(tx.get("date", ""))) or created_at.strftime("%Y-%m-%d")
                tx_year = int(tx_date[:4]) if tx_date else created_at.year

                tx_values.append((
                    tx_id,
                    stmt_id,
                    tx_date,
                    str(safe_extract(tx, ["description", "narration", "details"]) or "")[:255],
                    str(tx.get("amount", "")) if tx.get("amount") is not None else None,
                    str(tx.get("type", ""))[:10] if tx.get("type") else None,
                    str(tx.get("time", ""))[:8] if tx.get("time") else None,
                    hashlib.sha256(json.dumps(tx, sort_keys=True).encode()).hexdigest(),
                    created_at,
                    tx_year
                ))

            if tx_values:
                cursor.executemany("""
                    INSERT INTO transactions (
                        id, statement_id, date, description, amount, type, time,
                        content_hash, created_at, archive_year
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE id=id
                """, tx_values)
                result["inserted_rows"] += cursor.rowcount

        conn.commit()
        result.update({
            "success": True,
            "message": "Data saved successfully",
            "statement_id": stmt_id.hex(),
            "parsed_data": parsed_data,
            "from_cache": False
        })

    except Error as e:
        if conn:
            conn.rollback()
        result["message"] = f"Database error: {e.errno} - {e.msg}"
        if e.errno == 1062:
            result["is_duplicate"] = True
    except Exception as e:
        if conn:
            conn.rollback()
        result["message"] = f"Unexpected error: {str(e)}"
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

    return result


def get_statement_by_bank_and_last4(bank: str, last4: Optional[str] = None) -> Optional[Dict]:
    conn = cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        query = """
            SELECT id, bank, Card_number, Name, Email, Meta_Data, created_at
            FROM userDocumentParser
            WHERE bank = %s
        """
        params = [bank]

        if last4:
            query += " AND RIGHT(Card_number, 4) = %s"
            params.append(last4)

        query += " ORDER BY created_at DESC LIMIT 1"
        cursor.execute(query, tuple(params))
        row = cursor.fetchone()

        if not row:
            return None

        return {
            "statement_id": row["id"].hex(),
            "bank": row["bank"],
            "card_last4": row["Card_number"][-4:] if row["Card_number"] else None,
            "name": row["Name"],
            "email": row["Email"],
            "metadata": json.loads(row["Meta_Data"]),
            "created_at": row["created_at"].strftime("%Y-%m-%d %H:%M:%S")
        }

    except Exception as e:
        print(f"DB fetch error: {e}")
        return None
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
