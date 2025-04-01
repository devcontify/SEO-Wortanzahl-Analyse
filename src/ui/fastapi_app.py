from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import os
import sys
import pandas as pd
from typing import List, Dict

# Projektverzeichnis zum Python-Pfad hinzufügen
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, project_root)

from src.core.word_counter import WordCounter

app = FastAPI()

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.post("/analyze/")
async def analyze_files(files: List[UploadFile] = File(...)):
    results = []
    for uploaded_file in files:
        if uploaded_file.size > 10 * 1024 * 1024:  # 10MB limit
            raise HTTPException(status_code=400, detail=f"File {uploaded_file.filename} exceeds size limit")
            
        temp_path = os.path.join(project_root, 'temp', uploaded_file.filename)
        os.makedirs(os.path.dirname(temp_path), exist_ok=True)
        
        with open(temp_path, 'wb') as f:
            f.write(await uploaded_file.read())
        
        result = WordCounter.count_words(temp_path)
        result['file'] = uploaded_file.filename
        results.append(result)
        
        os.remove(temp_path)
    
    return {"results": results}

@app.get("/", response_class=HTMLResponse)
async def main():
    return """
    <html>
        <head>
            <title>SEO Wortanzahl-Analyse</title>
        </head>
        <body>
            <h1>📊 SEO Wortanzahl-Analyse</h1>
            <form action="/analyze/" enctype="multipart/form-data" method="post">
                <input name="files" type="file" multiple accept=".docx">
                <button type="submit">Analyze</button>
            </form>
        </body>
    </html>
    """