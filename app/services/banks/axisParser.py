import pdfplumber
import os
import traceback
from dotenv import load_dotenv
load_dotenv()


PDF_PASSWORD = os.getenv("PASSWORD_AXIS")
def parse_axis_credit_card_from_pdf(pdf_path: str):
    User_Details={}
    # Summary={}
    Account_summary={}
    Transactions=[]
    Rewards={}
    Total_Payment_Due={}
    error=None
    metadata={}

    try:
        with pdfplumber.open(pdf_path,password=PDF_PASSWORD) as pdf:
            full_text=""
            for page in pdf.pages:
                page_text=page.extract_text()
                if page_text:
                    full_text+=page_text+"\n"
            if not full_text.strip():
                raise ValueError("PDF has no extractable text")
    except Exception as e:
        error = f"Failed to open or extract PDF: {e}"
        
        print(error)
        return{
            "summary": {},
            "transactions": [],
            "bank": "Unknown",
            "error": error
        }        
    
    lines = [line.strip() for line in full_text.splitlines() if line.strip()]
    # print(lines)

    for idx,line in enumerate(lines):
    #   print("[[[[[[[[[[[[[[[[[[[]]]]]]]]]]]]]]]]]]]",idx,"\n")
    #   print(",,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,",line)
      try:
        User_Details["Credit_card"]=lines[0]
      except Exception as e:
          print(e)
          pass
      

      try:
       Name=lines[1]
       User_Details["Name"]=Name
      except Exception as e:
              print(e)
              pass    
      
    #         #   print(S)
    #           if idx==2:
    #         #    Address[]
    #            i=1
    #            for i in lines:
    #               value=lines[idx+i].strip()
    #               i+=1
    #               Summary["Address"]=Address.append(value)
                
      if "PAYMENT SUMMARY" in line:
          parts=lines[idx+2]
          value=parts.split()
        #   print(value)
          Account_summary["Total_payment_dues"]=value[0]+value[1]
          Account_summary["Minimum Payment Due"]=value[2]+value[3]
          Account_summary["Statement Period"]=value[4]+value[5]+value[6]
          Account_summary["Payment_due_date"]=value[7]
          Account_summary["Statement_date"]=value[8]
        #   Account_summary[""]=value[]

      if line.startswith(lines[1]):
       address = ""
       i = 1
       while idx + i < len(lines):
        next_line = lines[idx + i]
        if "PAYMENT SUMMARY" in next_line:
            break
        address += next_line.strip() + " "
        i += 1
        User_Details["Address"] = address.strip()
 
              
      elif line.startswith("Credit Card Number"): 
          parts=lines[idx+2].split()
        #   print(parts)   
          Account_summary["Card_number"]=parts[0]
          Account_summary["Credit_limit"]=parts[1]
          Account_summary["Available_credit_limit"]=parts[2]
          Account_summary["Available_cash_limit"]=parts[3]
          
      elif line.startswith("Previous Balance - Payments - Credits + Purchase + Cash Advance + Other Debit&Charges =Total Payment Due"):
          parts=lines[idx+2].split()
        #   print(parts) 
          Account_summary["Previous_Balance"]=parts[0]+parts[1]
          Account_summary["Payments"]=parts[2]
          Account_summary["Credits"]=parts[3]
          Account_summary["Purchase"]=parts[4]           
          Account_summary["Cash Advance"]=parts[5]
          Account_summary["Other Debit&Charges"]=parts[6]
          Total_Payment_Due["Total_payment_due"]=parts[7]+parts[8]

      elif line.startswith("eDGE REWARD"):
          parts=lines[idx+3].split()
        #   print(parts)  
          Rewards["eDGE REWARD POINTS"]=parts[0]
          Rewards["BALANCE AS ON DATE"]=parts[1]
          Rewards["CUSTOMER ID"]=parts[2]

      
      months = [str(m).zfill(2) for m in range(1, 13)]
      date_prefixes = [f"{str(d).zfill(2)}/{m}" for d in range(1, 32) for m in months]

      if any(line.startswith(d) for d in date_prefixes):
        try:
          parts = line.split()
        # print(parts)

          date = parts[0]
        # print("Date:",date) 

          raw_amount = parts[-2]  
        # print("Raw Amount:",raw_amount)

          txn_suffix = parts[-1].strip() 
          txn_suffix=txn_suffix.lower()
          txn_type = txn_suffix if txn_suffix.lower() in ["cr", "dr"] else ""

          amount = raw_amount.replace(",", "").strip()
        # print("Amount:",amount)

          description = " ".join(parts[1:-2])  
        # print("Description:",description)

          Transactions.append({
            "date": date,
            "description": description,
            "amount": amount,
            "type": txn_type
        })

        except Exception as e:
          print("Error:", e)
          pass

  
    return{
          "User_Details":User_Details,
          # "Summary":Summary,
          "Account_summary":Account_summary,
          "Total_Payment_Due":Total_Payment_Due,
          "transactions":Transactions,
          "Rewards":Rewards,
          "bank":metadata.get("bank","AXIS_BANK")
      }
