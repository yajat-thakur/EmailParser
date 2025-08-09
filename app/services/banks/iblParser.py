import pdfplumber
import os
import re
from dotenv import load_dotenv
load_dotenv()
PDF_PASSWORD = os.getenv("PASSWORD_IBL")


def parse_ibl_credit_card_from_pdf(pdf_path: str):
    User_Details = {}
    Rewards = {}
    Account_Summary = {}    
    Transactions = []
    metadata = {}
    error = None

    try:
        with pdfplumber.open(pdf_path, password=PDF_PASSWORD) as pdf:
            full_text = ""
            for page in pdf.pages:
                page_text=page.extract_text()
                if page_text:
                    full_text+=page_text + "\n"
        if not full_text.strip():
            raise ValueError("PDF has no extractable text")

    except Exception as e:
        error = f"Failed to open or extract PDF: {e}"
        (error)
        return {
            "summary":{},
            "transactions":[],
            "bank":"Unknown",
            "error":error
        }

    lines = [line.strip() for line in full_text.splitlines() if line.strip()]

    for idx,line in enumerate(lines):
        #   print("dddddddddddddddddddddddddddddddddd",idx,"\n")
        #   print("fffffffffffffffffffffffffffffffff",line)
        try:
            User_Details["Credit_card"] = lines[0]

        except Exception as e:
            print(e)

        if "Previous Balance" in line:
            parts = lines[idx+1].strip()
            Account_Summary["Previous_Balance"] = parts

        if "Purchases & Other Charges" in line:
            parts = lines[idx + 1].strip()
            Account_Summary["Purchases & Other Charges"] = parts

        if "Payment & Other Credits" in line:
            parts = lines[idx - 1].strip()
            Account_Summary["Cash Advance"] = parts

        if "Payment & Other Credits" in line:
            parts = lines[idx + 1].split()
            Account_Summary["Payment & Other Credits"] = parts[-1]

        if "Credit Limit" in line:
            parts = lines[idx + 2].split()
            if len(parts) <= 4:
                Account_Summary["Credit_limit"] = parts[-4]
                Account_Summary["Available_credit_limit"] = parts[-3]
                Account_Summary["Cash_limit"] = parts[-2]
                Account_Summary["Available_cash_limit"] = parts[-1]

        if "Minimum Amount Due" in line:
            parts = lines[idx + 1].split()
            if len(parts) == 1:
                Account_Summary["minimum_due"] = parts[0]

        if "ACCOUNTSUMMARY" in line:
            parts = lines[idx - 1]
            Account_Summary["Payment_due_date"] = parts

        if "Rewards OpeningBalance(Points)" in line:
            parts = lines[idx - 1].strip()
            Account_Summary["Total_payment_dues"] = parts

        if "Points" in line:
            parts = lines[idx].split("Points")
            if len(parts) <= 4:
                Account_Summary["Satement_Period"] = parts[-1]

        if "NOTE:*TotalofpointsredeemedbyyouandpointsforfeitedbytheBank(ifany)" in line:
            parts = lines[idx + 1]
            User_Details["Name"] = parts

        months = [str(m).zfill(2) for m in range(1, 13)]
        date_prefixes = [f"{str(d).zfill(2)}/{m}" for d in range(1, 32) for m in months]

        if "Statement Date" in line:
            i=1
            while idx+i<len(lines):
                parts=lines[idx + i].strip()
                match=re.search(r"\b\d{2}/\d{2}/\d{4}\b", parts)
                if match:
                    date_found=match.group()
                    Account_Summary["Statement_date"]=date_found
                    break
                i+=1

    count=0

    for idx,line in enumerate(lines):

        if "Summary" in line:
            count+=1

            if count==2:
                if idx+1<len(lines):
                    parts=lines[idx + 1].split()
                    Rewards["Opening Balance(Points)"]=parts[-4]
                    Rewards["Points Earned"]=parts[-3]
                    Rewards["Points Redeemed*"]=parts[-2]
                    Rewards["Closing Balance(Points)"]=parts[-1]

    address=""
    for idx,line in enumerate(lines):

        if "NOTE:*TotalofpointsredeemedbyyouandpointsforfeitedbytheBank(ifany)" in line:

            i=2
            while idx+i<len(lines):
                current_line=lines[idx + i]
                if "GSTIN:" in current_line:
                    break
                address+=current_line.strip() + " "
                i+=1
            break

    User_Details["Address"]=address

    # print("jjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjj")
    #  print("fkefdsjknjhagdhgvasjhbcghavcdghavdgh")
    start_parsing = False

    for idx, line in enumerate(lines):
     line = line.strip()

   
     if not start_parsing:
        if "ACCOUNTSUMMARY" in line.upper():
            start_parsing = True
        continue

    
     months = [str(m).zfill(2) for m in range(1, 13)]
     date_prefixes = [f"{str(d).zfill(2)}/{m}" for d in range(1, 32) for m in months]

     if any(line.startswith(d) for d in date_prefixes):
        parts = line.replace(",", "").replace("Total","").replace("Outstanding","").split()
        # print(parts)

        if len(parts) < 4:
            continue  

        date = parts[0]
        txn_type = parts[-1].lower()
        amount = parts[-2]
        description = " ".join(parts[1:-3])
        # print(descriptio
        # n)




        time = ""
        if ":" in parts[1]:
            time = parts[1]
            description = " ".join(parts[2:-2])

        Transactions.append({
            "date": date,
            "time": time,
            "description": description,
            "amount": amount,
            "type": txn_type
        })

        #  except Exception as e:
        #    print(e)
        #    pass
    return {
        "User_Details":User_Details,
        "Account_Summary":Account_Summary,
        "Rewards":Rewards,
        "transactions":Transactions,
        "bank":metadata.get("bank", "IBL_Bank")
    }
