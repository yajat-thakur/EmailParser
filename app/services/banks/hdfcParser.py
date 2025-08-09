import pdfplumber
import traceback
import os
# from datetime import datetime
from dotenv import load_dotenv
load_dotenv()
PDF_PASSWORD = os.getenv("PASSWORD_HDFC")
def parse_hdfc_credit_card_from_pdf(pdf_path: str):
    User_Details={}
    # summary={}
    # Statement_Credit_Card={}
    Account_Summary={}
    # Past_Dues={}
   #  Neu_Coins_Summary={}
   #  Bonus_NeuCoins_Symmary={}
    Transactions=[]
   #  Transactions2={}
    metadata={}
    error=None
    

    try:
        
        with pdfplumber.open(pdf_path, password=PDF_PASSWORD) as pdf:
            full_text=""
            for page in pdf.pages:
               # print(page)
                page_text = page.extract_text()
               # print(page_text)
                if page_text:
                    full_text+= page_text+"\n"
                   # print("===============>>>",full_text)
        if not full_text.strip():
            raise ValueError("PDF has no extractable text")
    except Exception as e:
        error = f"Failed to open or extract PDF: {e}"
        print(error)
        return {  
            "summary": {},
            "transactions": [],
            "bank": "Unknown",
            "error": error
        }
    
    lines = [line.strip() for line in full_text.splitlines() if line.strip()]
   #  print(lines)

    for idx,line in enumerate(lines):
        # print("--------------------",idx,"\n")
        # print("===================",line)
        # if line.startswith("Tata"):
        try:
             User_Details["Credit_card"]=lines[0].replace("0","")
        except Exception as e:
                print("line 0",e)
                pass
                


        if "HDFC Bank Credit Cards GSTIN" in line:
            try:
                User_Details["Credit Card Statements"]=lines[1]

            except Exception as e:
                print("HDFC Bank Credit Cards GSTIN",e)
                pass

        elif "Name" in line:
            try:
                User=""
                value_index=lines[idx]
                #print(value_index)
                value=value_index.replace(":","").split()
                #print(value)
                name_parts=[]
                if len(value)>2:
                 name_parts.append(value[2])
                #  print(User_Details1)
                if len(value)>3:
                 name_parts.append(value[3])
                #  print(User_Details2)
                if len(value)>4 and value[4].lower() not in ["statement"]:
                 name_parts.append(value[4])
                #  print(User_Details3)
                if name_parts:
                    User = " ".join(name_parts)
                    print("Extracted Name:", User)
                    User_Details["Name"] = User
                else:
                 print("No name parts found in line:", line)
                User_Details["Name"]=User              
                  # if len(value)>5:
                #    summary["Statement"]=value[4]
                
            except Exception as e:
                print("Name 1",e)
                pass

        elif "Email" in line:
          try:
            if "Email" not in User_Details: 
              value_index = lines[idx]
            #   print(value_index)
              value = value_index.replace(":", "").split()
            #   print("emailllllllllllllllll", value)

              User_Details["Email"] = value[1]

              value1 = 4  
              card_numbers = [] 

              while value1 < len(value):
                # print(value1)
                card_numbers.append(value[value1])
                value1 += 1

              Account_Summary["Card_number"] = " ".join(card_numbers)
          except Exception as e:
            print("Email",e)
            pass
 
        if ("Name") in line:
           try:
              value_index=lines[idx+1]
              value=value_index.strip()
            #   print(value)
              Account_Summary["AAN"]=value
           except Exception as e:
              print(e)
              pass   
           
        elif ("AAN") in line:
           try:
              value_index=lines[idx]
              value=value_index.split()
              Account_Summary["AAN"]=value[-1] 
           except Exception as e:
              print("Name 2",e)
              pass
              
        if "Statement Date" in line:
           try:
              value_index=lines[idx]
              value=value_index.split()
            #   print(value)
              Account_Summary["Statement_date"]=value[-4].replace("Date:","")
           except Exception as e:
              print("Address.....",e)   
              pass  
            
           
        if "please write a letter" in line:
         try:
             
             value_index = lines[idx]
             value=value_index.split()
            #  print(value)
             Account_Summary["Payment_due_date"]=value[-3]
             Account_Summary["Total_payment_dues"]=value[-2]
             Account_Summary["Minimum Amount Due"]=value[-1]
         except Exception as e:
            #  print("..........",e)
             pass   


        elif "Address" in line:
         try:
          value_index = lines[idx]
          # if value_index:  
          value = value_index.replace("Address :", "").replace("0","").strip()
          # elif value_index:
          #   value = value_index.replace("0 Address :", "").strip() 
     
          tokens = value.split()

          clean_tokens = []
          skip_next = False
          for i, token in enumerate(tokens):
            if skip_next:
                skip_next = False
               #  print(skip_next)
                continue

            if token == "Statement" and i+1 < len(tokens) and tokens[i+1].startswith("Date:"):
              
                skip_next = True
                continue
            elif token == "AAN" and i+1 < len(tokens) and tokens[i+1].startswith(":"):
               
                skip_next = True  
                continue
            elif token == ":" and i > 0 and tokens[i - 1] == "AAN":
              
                skip_next = True
                continue
            elif token.startswith("Date:") or token.count("/") == 2:
             
                continue
            elif token.replace(":", "").isdigit() and tokens[i - 1] == ":":
                
                continue
            else:
                clean_tokens.append(token)

          value = " ".join(clean_tokens)

        
          value += " " + lines[idx+1].strip()
          value += " " + lines[idx+2].strip()

          value = value.replace("Payment Due Date Total Dues Minimum Amount Due", "")
          User_Details["Address"] = value.strip()
         except Exception as e:
          print("Address", e)
          pass

 

                         
           
        elif line.startswith("Credit Limit"):
           try:
                parts=lines[idx+1].split()
                # print(parts)
                Account_Summary["Credit_limit"]=parts[-3]
                Account_Summary["Available_credit_limit"]=parts[-2]
                Account_Summary["Available_cash_limit"]=parts[-1]

           except Exception as e:
              print("Credit Limit",e)
              pass
           
        elif "Account Summary" in line :
           try:
              parts=lines[idx+5].split()
            #   print(parts)
              Account_Summary["Opening Balance"]=parts[-5]
              Account_Summary["Payment/Credits"]=parts[-4]
              Account_Summary["Purchase/Debits"]=parts[-3]
              Account_Summary["Finance Charges"]=parts[-2]
              Account_Summary["Total Dues"]=parts[-1]
           except Exception as e:
              print("Balance Credits Debits Charges",e)
              pass  
            
        elif "Past Dues (If any)" in line:
           parts=lines[idx+4].split()
        #    print(parts)

           Account_Summary["Overlimit"]=parts[-6]
           Account_Summary["3 Months+"]=parts[-5]
           Account_Summary["2 Months"]=parts[-4]
           Account_Summary["1 Month"]=parts[-3]
           Account_Summary["Current Dues"]=parts[-2]
           Account_Summary["Minimum Amount Due"]=parts[-1]


        elif "GST No" in line:
           try:
              parts=lines[idx]
              parts_value=parts.replace(":","").split()
              #print(parts_value)
              User_Details["GST No"]=parts_value[-1]
           except Exception as e:
              print(e)
              pass
           
      #   date_prefixes = [f"{str(d).zfill(2)}/" for d in range(1, 32)]
      #   print(date_prefixes)
      #   
        months = [str(m).zfill(2) for m in range(1, 13)]
        date_prefixes = [f"{str(d).zfill(2)}/{m}" for d in range(1, 32) for m in months]

        if any(line.startswith(d) for d in date_prefixes):
         # print("line starts with date")
         try:
           parts = line.split()

           date = parts[0]

        
           if len(parts) > 1 and ":" in parts[1]:
            time = parts[1]
            desc_start_index = 2
           else:
            time = ""
            desc_start_index = 1

           raw_amount = parts[-1].strip()
          #  raw_amount=raw_amount.lower()

        
           if raw_amount.lower().endswith("cr") or raw_amount.lower().endswith("dr"):
            amount = raw_amount[:-2].replace(",", "").strip()
            txn_type = "cr" if raw_amount.lower().endswith("cr") else "dr"
           else:
            amount = raw_amount.replace(",", "").strip()
            txn_type = ""

        
           description = " ".join(parts[desc_start_index:-1])

           Transactions.append({
            "date": date,
            "time": time,
            "description": description,
            "amount": amount,
            "type": txn_type
          })

         except Exception as e:
           print(e)
           pass


       
         #   Transactions["Transactions"]=parts[0]+" "+"|"+(parts[1]+" "+parts[2])+" "+"|"+lines[idx+1]+" "+"|"+parts[3]
         #   print(T)
       

   

   # replce
      #   if "Date" in line:
      #    i = 1 
      #    j = 0
      #    for i,j in lines:
      #     if (j == 0):
      #      parts=lines[idx+i].strip()
      #      Transactions[""]=parts
      #      i+=1
      #     j+=1

      #   if any(line.startswith(d) for d in ["13/", "12/", "11/", "04/"]):  
      #    # count+=1
      #    # print(count)
      #       try:
      #           parts = line.split()
      #           date = parts[0]
      #           amount = parts[-1].strip()
      #           Base_NeuCoins=parts[-2].strip()
      #           description = parts[-3].strip()
      #           Transactions.append({
      #               "Date": date,
      #               "Description": description,
      #               "Base NeuCoins*/ Feature_Reward_Points" : Base_NeuCoins,
      #               "Amount": amount,
      #               "type":type
      #           })
      #       except:
      #           continue   
        
                
        

           
        # if line.startswith("Name"):
        #     try:
        #      parts=lines[idx]
        #      print(parts)
        #      parts_value=parts.replace(" ","").replace(":","").split()
        #      summary["Name"]=parts_value
        #     except Exception as e:
        #         print(e)
        #         pass

    return{
        # "Credit_Card":Credit_card,
        # "Summary":summary,
        "User_Details":User_Details,
        # "Statement_Credit_Card":Statement_Credit_Card,
        "Account_Summary": Account_Summary,
        # "Past_Dues":Past_Dues,
        "transactions":Transactions,
      #   "Transactions2":Transactions2,
      #   "Neu_Coins_Summary":Neu_Coins_Summary,
      #   "Bonus_NeuCoins_Symmary":Bonus_NeuCoins_Symmary,
        "bank": metadata.get("bank", "HDFC Bank")


    }


