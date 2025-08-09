from app.services.banks import hdfcParser, iciciParser, sbiParser, kotakParser, iblParser, axisParser, yesParser
import os


def route_to_bank_parser(pdf_path: str, bank: str, statement_type: str):
    bank = bank.upper()
    statement_type = statement_type.lower()

    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"PDF not found at: {pdf_path}")

    if bank == "HDFC":
        if statement_type == "credit_card":
            return hdfcParser.parse_hdfc_credit_card_from_pdf(pdf_path)
        # elif statement_type == "bank":
        #     return hdfcParser.parse_hdfc_bank_statement_from_pdf(pdf_path)

    elif bank == "ICICI":
        if statement_type == "credit_card":
            return iciciParser.parse_icici_credit_card_from_pdf(pdf_path)
        # elif statement_type == "bank":
        #     return iciciParser.parse_icici_bank_statement_from_pdf(pdf_path)

    elif bank == "SBI":
        if statement_type == "credit_card":                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   
            
            return sbiParser.parse_sbi_credit_card_from_pdf(pdf_path)
        # elif statement_type == "bank":
        #     return sbiParser.parse_sbi_bank_statement_from_pdf(pdf_path)

    elif bank == "AXIS":
        if statement_type == "credit_card":
            return axisParser.parse_axis_credit_card_from_pdf(pdf_path)
        # elif statement_type == "bank":
        #     return axisParser.parse_axis_bank_statement_from_pdf(pdf_path)

    elif bank == "KOTAK":
        if statement_type == "credit_card":
            return kotakParser.parse_kotak_credit_card_from_pdf(pdf_path)
        # elif statement_type == "bank":
        #     return kotakParser.parse_kotak_bank_statement_from_pdf(pdf_path)

    elif bank == "IBL":
        if statement_type == "credit_card":
            return iblParser.parse_ibl_credit_card_from_pdf(pdf_path)
        # elif statement_type == "bank":
        #     return iblParser.parse_ibl_bank_statement_from_pdf(pdf_path)
    elif bank == "YES":
        if statement_type == "credit_card":
            return yesParser.parse_yes_credit_card_from_pdf(pdf_path)    

    else:
        raise NotImplementedError(f"Parsing for bank '{bank}' is not available yet.")

 
    raise ValueError(f"Invalid statement type '{statement_type}' for bank '{bank}'")
