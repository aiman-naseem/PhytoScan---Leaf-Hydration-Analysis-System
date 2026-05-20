from fastapi import FastAPI, UploadFile, File
import shutil
import os
from engine import analyze_plant_health

app = FastAPI()

@app.post("/scan")
async def scan_plant(file: UploadFile = File(...)):
    with open("temp.jpg", "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    status, score = analyze_plant_health("temp.jpg")
    return {"status": status, "health_percentage": score}