import pdfplumber
import os

def parse_sbi_credit_card_from_pdf(pdf_path: str):
   #  credit_card = {}
    User_Details= {}
    cash_back_amount = {}
    Account_Summary = {}
    Transactions = []
    metadata = {}

    try:
        with pdfplumber.open(pdf_path) as pdf:
            full_text = ""
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    full_text += page_text + '\n'
        if not full_text.strip():
            raise ValueError("PDF has no extractable text")
    except Exception as e:
        error = f"Failed to open or extract PDF: {e}"
        return {
            "summary": {},
            "transactions": [],
            "bank": "Unknown",
            "error": error
        }

    lines = [line.strip() for line in full_text.splitlines() if line.strip()]
   #  extracted = False

    for idx, line in enumerate(lines):
        # print("............................",idx,"\n")
        # print("//////////////////////////////",line)
        try:
            parts = lines[0].split()
            Account_Summary["Card_number"] = parts[5]
        except Exception as e:
            print(e)
            pass

        if "GSTIN of SBI Card" in line:
            try:
                parts = lines[idx + 1].strip()
                if "Credit Card Number" in parts:
                    name_part = parts.split("Credit Card Number")[0].strip()
                    User_Details["Name"] = name_part
                else:
                    User_Details["Name"] = parts

                User_Details["PLACE OF SUPPLY "] = lines[idx + 5].replace("PLACE OF SUPPLY :", "").strip()
                User_Details["STMT No."] = lines[idx + 7].replace("STMT No. :", "")
                Account_Summary["CKYC No."] = lines[idx + 8].replace("CKYC No. :", "").split()[-2]
                Account_Summary["Card_number"] = lines[idx + 2].strip()
                Account_Summary["Total_payment_dues"] = lines[idx + 4].strip()
                Account_Summary["Minimum_Amount_Due"] = lines[idx + 8].split()[-1]
                Account_Summary["Credit_limit"] = lines[idx + 11].split()[0]
                Account_Summary["Cash_limit"] = lines[idx + 11].split()[1]
                s1 = lines[idx + 11].split()[-3]
                s2 = lines[idx + 11].split()[-2]
                s3 = lines[idx + 11].split()[-1]
                Account_Summary["Statement_date"] = s1 + " " + s2 + " " + s3
                Account_Summary["Available_credit_limit"] = lines[idx + 13].split()[0]
                Account_Summary["Available_cash_imit"] = lines[idx + 13].split()[1]
                d1 = lines[idx + 13].split()[-3]
                d2 = lines[idx + 13].split()[-2]
                d3 = lines[idx + 13].split()[-1]
                Account_Summary["Payment_due_date"] = d1 + " " + d2 + " " + d3
               #         extracted = True

            except Exception as e:
                print(e)
                pass
        # if "PLACE OF SUPPLY" in line:


        if "ACCOUNT SUMMARY" in line:
            parts = lines[idx + 5].split()
            Account_Summary["Previous_Balance"] = parts[-5]
            Account_Summary["Payments,Reversals & other Credits"] = parts[-4]
            Account_Summary["Purchases & Other Debits"] = parts[-3]
            Account_Summary["Fee, Taxes & Interest Charges"] = parts[-2]
            Account_Summary["Total Outstanding"] = parts[-1]

        if "CARD CASHBACK SUMMARY FOR THIS STATEMENT" in line:
            parts = lines[idx + 4].split()
            cash_back_amount["cash_back_amount"] = parts[-1]

        
        months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
                  "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
        date_prefixes = [f"{str(d).zfill(2)} {month}" for d in range(1, 32) for month in months]

        
        if any(line.startswith(d) for d in date_prefixes):
            try:
                parts = line.split()
                d1, d2, d3 = parts[0], parts[1], parts[2]
                date = f"{d1} {d2} {d3}" if all([d1, d2, d3]) else ""

                raw_amount = parts[-2]
                txn_suffix = parts[-1].strip().lower().replace("c", "cr").replace("d", "dr")
                txn_type = txn_suffix if txn_suffix in ["cr", "dr"] else ""

                amount = raw_amount.replace(",", "").strip()
                description = " ".join(parts[3:-2])

                Transactions.append({
                    "date": date,
                    "description": description,
                    "amount": amount,
                    "type": txn_type
                })
            except Exception as e:
                print(e)

        
        elif len(line.split()) >= 2 and line.split()[-1].strip().lower() in ["d", "c"]:
            try:
                parts = line.split()
                raw_amount = parts[-2]
                txn_suffix = parts[-1].strip().lower().replace("c", "cr").replace("d", "dr")
                txn_type = txn_suffix if txn_suffix in ["cr", "dr"] else ""

                amount = raw_amount.replace(",", "").strip()
                description = " ".join(parts[:-2])

                Transactions.append({
                    "date": "",  
                    "description": description,
                    "amount": amount,
                    "type": txn_type
                })
            except Exception as e:
                print(f"Non-date txn parse error: {e}")

    return {
      #   "Credit_Card_Details": credit_card,
        "User_Details": User_Details,
        "Account_Summary": Account_Summary,
        "cash_back_amount": cash_back_amount,
        "transactions": Transactions,
        "bank": metadata.get("bank", "SBI_BANK")
    }
