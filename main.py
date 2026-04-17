from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class Part(BaseModel):
    width: int
    height: int
    qty: int

class RequestData(BaseModel):
    sheet_width: int
    sheet_height: int
    kerf: int
    parts: list[Part]

@app.get("/")
def root():
    return {"status": "SmartCut Engine Running"}

@app.post("/optimize")
def optimize(data: RequestData):
    total_area = 0
    for p in data.parts:
        total_area += p.width * p.height * p.qty

    sheet_area = data.sheet_width * data.sheet_height
    sheets = max(1, (total_area // sheet_area) + 1)

    waste = round(100 - ((total_area / (sheet_area * sheets)) * 100), 2)

    return {
        "sheets_needed": sheets,
        "waste_percent": waste,
        "message": "First version engine active"
    }
