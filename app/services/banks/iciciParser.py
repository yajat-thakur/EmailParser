# import pdfplumber
# import traceback
# from dotenv import load_dotenv
# load_dotenv()
# import os
# PDF_PASSWORD = os.getenv("PASSWORD_ICICI")

# def parse_icici_credit_card_from_pdf(pdf_path: str):
#     User_Details = {}
#     Rewards={}
#     Account_Summary={}
#     # Statement_Summary={}
#     # Credit_Summary={}
#     Transactiosn = []
#     metadata = {}
#     error = None

#     try:
#         with pdfplumber.open(pdf_path, password=PDF_PASSWORD) as pdf:
#             full_text = ""
#             for page in pdf.pages:
#                 page_text = page.extract_text()
#                 if page_text:
#                     full_text += page_text + "\n"

#         if not full_text.strip():
#             raise ValueError("PDF has no extractable text")

#     except Exception as e:
#         error = f"Failed to open or extract PDF: {e}"
#         print(error)
#         return {
#             "summary": {},
#             "Transactiosn": [],
#             "bank": "Unknown",
#             "error": error
#         }

  
#     lines = [line.strip() for line in full_text.splitlines() if line.strip()]


#     for idx, line in enumerate(lines):
#     #  print("iiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiii",idx,"\n")
#     #  print("llllllllllllllllllllllllllllllll",line)
       

#     #  if "MR VINEET KUMAR" in line.upper():
#      User_Details["Name"] = lines[2]
#      address_lines = []
#      address_lines = [lines[3].strip(), lines[4].strip(), lines[5].strip()]
#      User_Details["Address"] = " ".join(address_lines)
 

#      if "STATEMENT DATE" in line:
#             Account_Summary["Statement_date"] = lines[idx + 1]
 
#      elif "PAYMENT DUE DATE" in line:
#             Account_Summary["Payment_due_date"] = lines[idx + 1].strip()

     
          
#      elif "STATEMENT SUMMARY" in line:
#             try:
#             #  if "Total Amount due" not in line:
#              part=lines[idx+2].replace("₹", "").replace(",", "").replace("=","").replace("+","").replace("-","").strip()
#             #  print(part[0])
#              Account_Summary["Total_payment_due"] = part
#             except:
#                 pass
     

#      elif "Minimum Amount due" in line:
#            try: 
#             Account_Summary["minimum_due"] = lines[idx + 1].replace("₹", "").replace(",", "").strip()
#            except:
#                 pass 
     
#      elif line.startswith("Previous Balance"):
#                     try:
#                         parts = lines[idx + 1].split()
#                         if len(parts) >= 4:
#                             Account_Summary["Previous_Balance"] = parts[0].replace("₹", "").replace(",", "")
#                             Account_Summary["purchases_charges"] = parts[1].replace("₹", "").replace(",", "")
#                             Account_Summary["cash_advances"] = parts[2].replace("₹", "").replace(",", "")
#                             Account_Summary["payments_credits"] = parts[3].replace("₹", "").replace(",", "")
#                     except:
#                         pass    


#      elif line.startswith("Credit Limit (Including cash)"):
#           try:
#                value_index = lines[idx+2]
#                values = value_index.replace("₹","").split()

#                Account_Summary["Credit_limit"]=values[6]
#                Account_Summary["Available_credit_limit"]=values[7]
#                Account_Summary["Cash_limit"]=values[8]
#                Account_Summary["Available_cash_limit"]=values[9]
#           except Exception as e:
#                print(e)
#                pass
    

                         

#     #  elif "Credit Limit" in line and "Available Credit" in line:
#     #   try:
#     #     with pdfplumber.open(pdf_path, password=PDF_PASSWORD) as pdf:
#     #         for page in pdf.pages:
#     #             tables = page.extract_tables()
#     #             for table in tables:
#     #                 for row_idx, row in enumerate(table):
#     #                     if not row or len(row) < 4:
#     #                         continue
#     #                     cells = [c.strip() if c else "" for c in row]
#     #                     if (
#     #                         "Credit Limit" in cells[0]
#     #                         and "Available Credit" in cells[1]
#     #                         and "Cash Limit" in cells[2]
#     #                         and "Available Cash" in cells[3]
#     #                     ):
                            
#     #                         if row_idx + 1 < len(table):
#     #                             values = table[row_idx + 1]
#     #                             if len(values) >= 4:
#     #                                 summary["credit_limit"] = values[0].replace("₹", "").replace(",", "").strip()
#     #                                 summary["available_credit"] = values[1].replace("₹", "").replace(",", "").strip()
#     #                                 summary["cash_limit"] = values[2].replace("₹", "").replace(",", "").strip()
#     #                                 summary["available_cash"] = values[3].replace("₹", "").replace(",", "").strip()
#     #                         break
#     #             break  
#     #   except Exception as e:
#     #     print("Error reading credit summary:", e)


                        

          
#      #if not line:continue     

#      elif "ICICl Bank Rewards" in line:
#       try:
#          parts = lines[idx+1]
#          print(parts[1])
#          part = parts.replace(" ","").replace("|","").split()
         
#          Rewards["Total Points earned"] = parts[1]
#       except Exception as e:
#            print(e)
#            pass

#      elif "Points earned on iShop" in line:
#           try:
#             parts = lines[idx]
#             print(parts)
#             part=parts.replace(" ","").replace("|","").split()

#             Rewards["Points earned on iShop"]=parts[1]
#           except Exception as e:
#                     print(e)
#                     pass 
                    

#      elif "Statement period" in line:
#       part = line.split("Statement period")[-1] 
#       part = part.replace(":", "").strip()       

#       if "to" in part:
#         to_index = part.find("to")
        
#         first_date = part[:to_index].strip()
        
       
#         second_date_part = part[to_index + 2:].strip() 
#         second_date_words = second_date_part.split()[:3]  
#         second_date = " ".join(second_date_words)
        
#         Account_Summary["statement_period"] = f"{first_date} to {second_date}"

            

#      elif "Place of supply" in line:
#       part = line.split("Place of supply")[-1]  
#       part = part.replace(":", "").strip()      

#       if "l" in part:
#           part = part.split("l")[0].strip()

#       User_Details["place_of_supply"] = part


#      elif "ICICI Bank" in line and "Credit Cards" in line:
#             metadata["bank"] = "ICICI Bank"

#      months = [str(m).zfill(2) for m in range(1, 13)]
#      date_prefixes = [f"{str(d).zfill(2)}/{m}" for d in range(1, 32) for m in months] 
#      if any(line.startswith(d) for d in date_prefixes):  
#             try:
#                 parts = line.split()
#                 date = parts[0]
#                 amount = parts[-2].strip()
#                 typ=parts[-1].strip()
#                 type=typ.lower()
#                 description = " ".join(parts[1:-2])
#                 Transactiosn.append({
#                     "date": date,
#                     "description": description,
#                     "amount": amount,
#                     "type":type
#                 })
#             except:
#                 continue

#     return {
#         "User_Details": User_Details,
#         "Rewards":Rewards,
#         "Account_Summary":Account_Summary,
#         # "Credit_Summary":Credit_Summary,    
#         "transactiosn": Transactiosn,
#         "bank": metadata.get("bank", "ICICI Bank")
        
#     }




import pdfplumber
import traceback
from dotenv import load_dotenv
import os

load_dotenv()
PDF_PASSWORD = os.getenv("PASSWORD_ICICI")

def parse_icici_credit_card_from_pdf(pdf_path: str):
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
                words = page.extract_words(use_text_flow=True)

                # Filter out small or potentially invisible/overlapping words
                filtered_words = [
                    word for word in words
                    if float(word.get('top', 0)) > 0
                    and float(word.get('bottom', 0)) - float(word.get('top', 0)) > 4
                    and word.get('text', '').strip()
                ]

                # Sort by vertical (top) then horizontal (x0)
                filtered_words.sort(key=lambda w: (round(w['top']), w['x0']))

                current_y = None
                line = ""
                for word in filtered_words:
                    y = round(word['top'])
                    if current_y is None or abs(y - current_y) < 5:
                        line += word['text'] + " "
                    else:
                        full_text += line.strip() + "\n"
                        # print("iiiiiiiiiiiiiiii",full_text)
                        line = word['text'] + " "
                        # print("llllllllllllll",line)
                        current_y = y
                full_text += line.strip() + "\n"

        if not full_text.strip():
            raise ValueError("PDF has no extractable text")

    except Exception as e:
        error = f"Failed to open or extract PDF: {e}"
        print(error)
        return {
            "summary": {},
            "Transactions": [],
            "bank": "ICICI",
            "error": error
        }

    # Split text into cleaned lines
    lines = [line.strip() for line in full_text.splitlines() if line.strip()]

    for idx, line in enumerate(lines):
        # print(f"ppppppppppp") 
        #  # Abhi testing ke liye, tu yahan parsing kar sakta hai
          print("iiiiiiiiiiiiiiiiii",idx+1,"\n")
          print("lllllllllllllllll",line)
        #   if "" in line:
              

    return {
        "summary": Account_Summary, 
        "Transactions": Transactions,
        "bank": "ICICI",
        "error": None
    }
