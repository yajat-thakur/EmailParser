import os
import pdfplumber
import re
from dotenv import load_dotenv

load_dotenv()
PDF_PASSWORD = os.getenv("PASSWORD_YES")

def parse_yes_credit_card_from_pdf(pdf_path: str):
    User_Details = {}
    Rewards = {}
    Account_Summary = {}
    Transactiosn = []
    metadata = {}
    error = None

    try:
        with pdfplumber.open(pdf_path, password=PDF_PASSWORD) as pdf:
            full_text = ""
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    full_text += page_text + "\n"
        if not full_text.strip():
            raise ValueError("PDF has no extractable text")
    except Exception as e:
        error = f"Failed to open or extract PDF: {e}"
        print(error)
        return {
            "summary": {},
            "Transactiosn": [],
            "bank": "Unknown",
            "error": error
        }

    lines = [line.strip() for line in full_text.splitlines() if line.strip()]

    for idx, line in enumerate(lines):
        if idx == 1:
            User_Details["Credit_card"] = line

        if "Overview Statement Summary" in line:
            try:
                User_Details["Email"] = lines[idx - 1]
            except Exception:
                pass

        if "Card Number" in line:
            Account_Summary["Card_number"] = line.split()[-1]

        if "Registered Mobile Number" in line:
            try:
                Account_Summary["Mobile_number"] = lines[idx + 2].split()[-1]
            except Exception:
                pass

        if "Statement Period" in line:
            try:
                parts = lines[idx + 1].split()
                Account_Summary["Statement_Period"] = parts[-8] + " TO " + parts[-10]
                Account_Summary["Credit_limit"] = parts[-6]
            except Exception:
                pass

        if "Statement Date" in line:
            try:
                Account_Summary["Current_Purchases / Cash_Advance"] = line.split("Rs.")[-1]
                Account_Summary["Available_credit_limit"] = line.split("Rs.")[-2]
                Account_Summary["Statement_date"] = line.replace("Statement Date :", "").split("Rs.")[-3]
            except Exception:
                pass

        if "Total Amount Due" in line:
            try:
                Account_Summary["Points_earned"] = line.split()[-1]
                Account_Summary["Total_payment_dues"] = lines[idx + 1].replace("Rs.", "").split()[-2]
                Account_Summary["Credit_limit"] = lines[idx + 1].replace("Rs.", "").split()[-1]
            except Exception:
                pass

        if "Minimum Amount Due" in line:
            try:
                Account_Summary["Payment & Credits_Received"] = line.split()[-1]
                Account_Summary["minimum_due"] = lines[idx + 1].replace("Rs.", "").split()[-2]
                Account_Summary["Available_cash_limit"] = lines[idx + 1].replace("Rs.", "").split()[-1]
            except Exception:
                pass

        if "Payment Due Date" in line:
            try:
                Account_Summary["Payment_due_date"] = line.replace("Payment Due Date:", "").split()[0]
            except Exception:
                pass

        if "Previous Balance" in line:
            try:
                Account_Summary["Previous_Balance"] = lines[idx + 1]
            except Exception:
                pass

        if "Points earned so far" in line:
            try:
                parts = lines[idx + 1].split()
                Rewards["Points earned so far"] = parts[0]
                Rewards["Points earned this month"] = parts[1]
                Rewards["Points redeemed this month"] = parts[2]
                Rewards["Points available for redemption"] = parts[3]
            except Exception:
                pass

        if "Registered Mobile Number" in line:
            try:
                no_digits = re.sub(r'\d+', '', line)
                name_part = no_digits.split("Registered Mobile Number")[0]
                name_part = re.sub(r'\s+', ' ', name_part).strip()
                words = name_part.split()
                merged = []
                buffer = ''
                for word in words:
                    if len(word) == 1:
                        buffer += word
                    else:
                        if buffer:
                            merged.append(buffer)
                            buffer = ''
                        merged.append(word)
                if buffer:
                    merged.append(buffer)
                User_Details["Name"] = ' '.join(merged)
            except Exception:
                pass

    address_lines = []
    collect = False
    for idx, line in enumerate(lines):
        if "Registered Mobile Number" in line:
            collect = True
            continue

        if collect:
            line = line.strip()
            if not line or set(line) <= set("/[] "):
                continue
            if re.search(r'[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}', line):
                break
            if re.search(r'\+91[\dXx]{10}', line):
                line = re.sub(r'\+91[\dXx]{10}', '', line).strip()
                if line:
                    address_lines.append(line)
                continue
            if "Registered Email Id" in line:
                continue
            address_lines.append(line)

    address = ' '.join(address_lines).replace("Registered Email Id", "").strip()
    if address:
        User_Details["Address"] = address

    Transactiosn = []
    skip_next_line = False

    for idx, line in enumerate(lines):
        line = line.strip()
        if "Statement Period" in line:
            skip_next_line = True
            continue
        if skip_next_line:
            skip_next_line = False
            continue
        months = [str(m).zfill(2) for m in range(1, 13)]
        date_prefixes = [f"{str(d).zfill(2)}/{m}" for d in range(1, 32) for m in months]
        if any(line.startswith(d) for d in date_prefixes):
            try:
                parts = line.split()
                date = parts[0]
                next_line = lines[idx + 1].strip() if idx + 1 < len(lines) else ""
                txn_suffix = parts[-1].strip()
                txn_type = txn_suffix.lower() if txn_suffix.lower() in ["dr", "cr"] else ""
                amount = ""
                for i in range(len(parts) - 2, 0, -1):
                    amt = parts[i].replace(",", "").replace("₹", "")
                    if amt.replace(".", "").isdigit():
                        amount = parts[i]
                        break
                desc_parts = parts[1:]
                if amount:
                    desc_parts = [p for p in desc_parts if p != amount and p.lower() != txn_type]
                description = " ".join(desc_parts).strip() +" "+ next_line.strip()
                Transactiosn.append({
                    "date": date,
                    "description": description.strip(),
                    "amount": amount,
                    "type": txn_type
                })
            except Exception:
                continue

    return {
        "User_Details": User_Details,
        "Account_Summary": Account_Summary,
        "Rewards": Rewards,
        "transactiosn": Transactiosn,
        "bank": metadata.get("bank", "YES Bank")
    }
