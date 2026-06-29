import pdfplumber
import re

def parse_lc_pdf(pdf_path):
    """提取 PDF 文本并解析关键字段"""
    with pdfplumber.open(pdf_path) as pdf:
        text = ""
        for page in pdf.pages:
            text += page.extract_text() or ""
    
    # 以下为正则提取（比原代码更全面，支持 SWIFT 标签）
    def clean(s): return re.sub(r'\s+', ' ', s).strip()
    
    lc_number = re.search(r'(?:L/C NO|DOCUMENTARY CREDIT NUMBER)[\s:]*([A-Z0-9]+)', text, re.I)
    lc_number = clean(lc_number.group(1)) if lc_number else ""
    
    issuing_bank = re.search(r'(?:ISSUING BANK|:52A:)[\s:]*([^\n:]+)', text, re.I)
    issuing_bank = clean(issuing_bank.group(1)) if issuing_bank else ""
    
    applicant = re.search(r'(?:APPLICANT|:50:)[\s:]*([^\n:]+)', text, re.I)
    applicant = clean(applicant.group(1)) if applicant else ""
    
    beneficiary = re.search(r'(?:BENEFICIARY|:59:)[\s:]*([^\n:]+)', text, re.I)
    beneficiary = clean(beneficiary.group(1)) if beneficiary else ""
    
    amount = re.search(r'(?:AMOUNT|:32B:)[\s:]*([A-Z]{3}\s*[\d,\.]+)', text, re.I)
    amount = clean(amount.group(1)) if amount else ""
    
    expiry = re.search(r'(?:EXPIRY DATE|:31D:)[\s:]*(\d{6})', text, re.I)
    expiry = expiry.group(1) if expiry else ""
    
    latest_ship = re.search(r'(?:LATEST DATE OF SHIPMENT|:44C:)[\s:]*(\d{6})', text, re.I)
    latest_ship = latest_ship.group(1) if latest_ship else ""
    
    pol = re.search(r'(?:PORT OF LOADING|:44A:)[\s:]*([^\n:]+)', text, re.I)
    pol = clean(pol.group(1)) if pol else ""
    
    pod = re.search(r'(?:PORT OF DISCHARGE|:44B:)[\s:]*([^\n:]+)', text, re.I)
    pod = clean(pod.group(1)) if pod else ""
    
    goods = re.search(r'(?:DESCRIPTION OF GOODS|:45A:)[\s:]*([\s\S]+?)(?=:46A:|:47A:|$)', text, re.I)
    goods = clean(goods.group(1)) if goods else ""
    
    docs_req = re.search(r'(?:DOCUMENTS REQUIRED|:46A:)[\s:]*([\s\S]+?)(?=:47A:|$)', text, re.I)
    docs_req = clean(docs_req.group(1)) if docs_req else ""
    
    additional = re.search(r'(?:ADDITIONAL CONDITIONS|:47A:)[\s:]*([\s\S]+?)(?=:71D:|$)', text, re.I)
    additional = clean(additional.group(1)) if additional else ""
    
    # 解析 46A 中的单据清单（简易版）
    doc_list = []
    if docs_req:
        parts = re.split(r'\d+\)|[\+\-]', docs_req)
        for part in parts:
            part = part.strip()
            if not part: continue
            # 提取份数
            orig = re.search(r'(\d+)\s*ORIGINAL', part, re.I)
            orig = int(orig.group(1)) if orig else 1
            copy = re.search(r'(\d+)\s*COP', part, re.I)
            copy = int(copy.group(1)) if copy else 0
            # 取第一句作为名称
            name = re.split(r',|AND|WITH', part)[0].strip()
            if name:
                doc_list.append({"name": name, "originals": orig, "copies": copy})
    
    return {
        "lc_number": lc_number,
        "issuing_bank": issuing_bank,
        "applicant": applicant,
        "beneficiary": beneficiary,
        "amount": amount,
        "expiry": expiry,
        "latest_shipment": latest_ship,
        "port_loading": pol,
        "port_discharge": pod,
        "goods_description": goods,
        "docs_required": docs_req,
        "additional_conditions": additional,
        "document_list": doc_list
    }
