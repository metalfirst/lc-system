from datetime import datetime

def analyze_risks(parsed):
    risks = []
    # 1. 软条款关键词（申请人控制）
    soft_keywords = [
        "INSPECTION CERTIFICATE ISSUED BY APPLICANT",
        "CERTIFICATE OF QUALITY ISSUED BY APPLICANT",
        "SIGNED BY APPLICANT",
        "APPROVAL OF APPLICANT",
        "RELEASE OF GOODS WITHOUT B/L"
    ]
    additional = parsed.get("additional_conditions", "").upper()
    for kw in soft_keywords:
        if kw in additional:
            risks.append({
                "level": "critical",
                "message": f"检测到高风险软条款：{kw}，极易导致付款延迟或拒付！"
            })
    
    # 2. 时间逻辑
    today = datetime.now().strftime("%y%m%d")
    latest = parsed.get("latest_shipment")
    if latest and latest < today:
        risks.append({
            "level": "error",
            "message": f"最迟装运日 {latest} 已过，当前日期 {today}，无法满足信用证要求！"
        })
    expiry = parsed.get("expiry")
    if expiry and expiry < today:
        risks.append({
            "level": "error",
            "message": f"信用证有效期 {expiry} 已过，单据将无法承兑！"
        })
    
    # 3. 银行名称简单判断（可扩展）
    bank = parsed.get("issuing_bank", "").upper()
    if "BANK" not in bank:
        risks.append({
            "level": "warning",
            "message": "开证行名称疑似不完整，请核实是否为正规银行。"
        })
    
    return risks
