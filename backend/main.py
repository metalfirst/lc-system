import os
import shutil
import zipfile
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from utils.parser import parse_lc_pdf
from utils.risk_check import analyze_risks
from utils.doc_generator import generate_all_docs
import uuid

app = FastAPI()

# 允许跨域（供 GitHub Pages 前端调用）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境请替换为你的前端域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/parse")
async def parse_pdf(file: UploadFile = File(...)):
    """解析信用证 PDF，返回提取字段和风险提示"""
    if not file.filename.endswith('.pdf'):
        raise HTTPException(400, "仅支持 PDF 文件")
    
    # 保存临时文件
    temp_path = f"/tmp/{uuid.uuid4()}.pdf"
    with open(temp_path, "wb") as f:
        shutil.copyfileobj(file.file, f)
    
    try:
        # 1. 提取文本并解析字段
        parsed = parse_lc_pdf(temp_path)
        # 2. 风险分析
        risks = analyze_risks(parsed)
        return {
            "status": "success",
            "data": parsed,
            "risks": risks
        }
    except Exception as e:
        raise HTTPException(500, f"解析失败: {str(e)}")
    finally:
        os.remove(temp_path)

@app.post("/generate")
async def generate_docs(request: dict):
    """根据用户补充信息和解析结果生成全套 Word 文档，返回 ZIP 下载"""
    parsed = request.get("parsed_data")
    form = request.get("form_data")  # 用户修改的字段
    if not parsed:
        raise HTTPException(400, "缺少信用证数据")
    
    zip_path = f"/tmp/{uuid.uuid4()}.zip"
    generate_all_docs(parsed, form, zip_path)
    
    return FileResponse(zip_path, media_type="application/zip", filename="LC_Documents.zip")
