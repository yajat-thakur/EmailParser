import pdfplumber

def parse_kotak_credit_card_from_pdf(pdf_path: str):
    Account_summary = {}
    Rewards = {}
    Transactions = []
    User_Details = {}
    metadata = {}

    try:
        with pdfplumber.open(pdf_path) as pdf:
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
            "Account_summary": {},
            "transactions": [],
            "bank": "Unknown",
            "error": error
        }

    lines = [line.strip() for line in full_text.splitlines() if line.strip()]
    date_prefixes = [f"{str(d).zfill(2)}/" for d in range(1, 32)]
    removal_keywords = ["Apparels", "Electronics", "Travel", "Dining", "Fuel", "Utilities"]

    for idx, line in enumerate(lines):
        try:
            if "StatementDate" in line:
                name_part = lines[0].split("StatementDate")[0].strip()
                User_Details["Name"] = name_part
        except Exception as e:
            print("Name extraction error:", e)

        if "StatementDate" in line:
            try:
                statement_date = line.split()[-1]
                User_Details["Statement_date"] = statement_date
            except Exception as e:
                print("Statement Date error:", e)

        if "Previous Payments Purchases" in line and "OpeningBalance" in line:
            try:
                parts = line.split()
                if parts:
                    Rewards["Opening Balance"] = parts[-1]
            except Exception as e:
                print("Opening Balance error:", e)

        if "Earnedthismonth" in line:
            try:
                parts = line.split()
                if parts:
                    Rewards["Earned this month"] = parts[-1]
            except Exception as e:
                print(e)

        if "Redeemedthismonth" in line:
            try:
                parts = line.split()
                if parts:
                    Rewards["Redeemed this month"] = parts[-1]
            except Exception as e:
                print(e)

        if "Expiredthismonth" in line:
            try:
                parts = line.split()
                if parts:
                    Rewards["Expired this month"] = parts[-1]
            except Exception as e:
                print(e)

        if "ClosingBalance" in line:
            try:
                parts = line.split()
                if parts:
                    Rewards["Closing Balance"] = parts[-1]
            except Exception as e:
                print(e)

        if "Expiringnextmonth" in line:
            try:
                parts = line.split()
                if parts:
                    Rewards["Expiring next month"] = parts[-1]
            except Exception as e:
                print(e)

        if "My Summary" in line and "MyRewards" in line:
            try:
                parts1 = lines[idx + 4].replace(",", "").replace("-", "").replace("+", "").replace("=", "").split()
                Account_summary["Previous Amount Due"] = parts1[0]
                Account_summary["Payments"] = parts1[1]
                Account_summary["Purchases &Other Charges"] = parts1[2]
                # Account_summary["Total_payment_due"] = parts1[3]
            except Exception as e:
                print(e)

        if "TotalCreditLimit (incl.cash)" in line:
            parts = line.replace("(incl.cash):", "").split()
            Account_summary["Credit_limit"] = parts[1]
            Account_summary["Cash_limit"] = parts[-1]

        if "SelfSetCreditLimit" in line:
            parts = lines[idx]
            if "(incl.cash):" or "(incl.cash) :" in line:
                parts = parts.replace("(incl.cash):", "").replace("(incl.cash) :", "").replace(":", "")
                parts = parts.split()
            else:
                parts = parts.replace(":", "").split()
            Account_summary["Self Set Credit Limit"] = parts[1]
            Account_summary["Available_cash_limit"] = parts[-1]

        if "AvailableCreditLimit" in line:
            parts = line
            if "(incl.cash):" or "(incl.cash) :" in line:
                parts = parts.replace("(incl.cash):", "").replace("(incl.cash) :", "").replace(":", "")
                parts = parts.split()
            else:
                parts = parts.replace(":", "").split()
            Account_summary["Available_credit_limit"] = parts[-1]

        if "MinimumAmountDue" in line:
            parts = line.split()
            Account_summary["Minimum_Amount_Due"] = parts[-1]

        if "TotalAmountDue" in line:
            parts = line.split()
            Account_summary["Total_payment_dues"] = parts[-1]

        if "RemembertoPayBy" in line:
            parts = line.split()
            Account_summary["Remember to PayBy"] = parts[-1]

        if "TotalOutstanding" in line:
            parts = lines[idx + 1].split()
            Account_summary["Total Outstanding"] = parts[-1]

        if "GSTIN-" in line:
            parts = line.replace("-", "").split()
            Account_summary["GSTIN"] = parts[-1]

        if "CustomerRelationshipNumber" in line:
            parts = line.replace(":-", "").split()
            Account_summary["Customer Relationship Number"] = parts[1]

        if "PrimaryCardNumber" in line:
            parts = line.split()
            Account_summary["Primary CardNumber"] = parts[1]

        address_lines = []
        part = ""
        stop_keywords = [
            "TotalAmountDue", "RemembertoPayBy", "GSTIN",
            "CustomerRelationshipNumber", "PrimaryCardNumber", "StatementDate",
            "TotalOutstanding", "My Account_summary", "Previous Payments", "Transaction"
        ]

        for i in range(1, len(lines)):
            l = lines[i].strip()
            if not l:
                continue
            if any(stop_kw in l for stop_kw in stop_keywords):
                break
            if not l.replace("Rs.", "").replace(" ", "").replace("-", "").replace(".", "").isdigit():
                address_lines.append(l)
            if "MinimumAmountDue" in l:
                part = l.split()[-1]

        if address_lines:
            address = " ".join(address_lines).replace("MinimumAmountDue", "")
            if part:
                address = address.replace(part, "")
            User_Details["Address"] = " ".join(address.split())



        months = [str(m).zfill(2) for m in range(1, 13)]
        date_prefixes = [f"{str(d).zfill(2)}/{m}" for d in range(1, 32) for m in months]
        line = line.strip()
        if not line:
            continue

        if "spends" in line.lower():
            continue

        if "total purchases" in line.lower() and "amount" in line.lower():
            try:
                parts = line.split()
                raw_amount = parts[-1]
                amount = raw_amount.replace(",", "").strip()
                if parts[-2].lower() == "amount":
                    description = " ".join(parts[:-2]).strip()
                else:
                    description = " ".join(parts[:-1]).strip()
                for keyword in removal_keywords:
                    description = description.replace(keyword, "")
                Transactions.append({
                    "date": "",
                    "description": " ".join(description.split()),
                    "amount": amount,
                    "type": ""
                })
            except Exception as e:
                print(f"Total Purchases parse error: {e}")
                

        elif any(line.startswith(d) for d in date_prefixes):
            try:
                parts = line.split()
                date = parts[0]
                txn_suffix = parts[-1].strip().lower()
                if txn_suffix in ["cr", "dr"]:
                    raw_amount = parts[-2]
                    txn_type = txn_suffix
                    amount = raw_amount.replace(",", "").strip()
                    description = " ".join(parts[1:-2]).strip()
                else:
                    raw_amount = parts[-1]
                    txn_type = ""
                    amount = raw_amount.replace(",", "").strip()
                    description = " ".join(parts[1:-1]).strip()
                for keyword in removal_keywords:
                    description = description.replace(keyword, "")
                Transactions.append({
                    "date": date,
                    "description": " ".join(description.split()),
                    "amount": amount,
                    "type": txn_type
                })
            except Exception as e:
                print(f"Date-based txn parse error: {e}")

        elif len(line.split()) >= 3 and line.split()[-1].strip().lower() in ["dr", "cr"]:
            try:
                parts = line.split()
                raw_amount = parts[-2]
                txn_suffix = parts[-1].strip().lower()
                txn_type = txn_suffix
                amount = raw_amount.replace(",", "").strip()
                description = " ".join(parts[:-2])
                for keyword in removal_keywords:
                    description = description.replace(keyword, "")
                Transactions.append({
                    "date": "",
                    "description": " ".join(description.split()),
                    "amount": amount,
                    "type": txn_type
                })
            except Exception as e:
                print(f"Non-date txn parse error: {e}")

    return {
        "User_Details": User_Details,
        "Account_summary": Account_summary,
        "Rewards": Rewards,
        "transactions": Transactions,
        "bank": metadata.get("bank", "KOTAK_BANK")
    }
