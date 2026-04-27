from fastapi import FastAPI
from pydantic import BaseModel
from typing import List

app = FastAPI()

# -------------------
# MODELS
# -------------------

class Part(BaseModel):
    width: int
    height: int
    qty: int
    rotate: bool = True

class RequestData(BaseModel):
    sheet_width: int
    sheet_height: int
    kerf: int
    parts: List[Part]

# -------------------
# HELPERS
# -------------------

def expand_parts(parts):
    result = []
    for p in parts:
        for _ in range(p.qty):
            result.append({
                "width": p.width,
                "height": p.height,
                "rotate": p.rotate
            })
    return result

def sort_parts(parts):
    return sorted(parts, key=lambda x: x["width"] * x["height"], reverse=True)

# -------------------
# SIMPLE PACKING
# -------------------

def place_on_sheet(sheet_w, sheet_h, kerf, parts):
    placed = []
    free_spaces = [(0, 0, sheet_w, sheet_h)]
    remaining = []

    for part in parts:
        placed_flag = False

        for i, space in enumerate(free_spaces):
            sx, sy, sw, sh = space

            options = [(part["width"], part["height"])]

            if part["rotate"]:
                options.append((part["height"], part["width"]))

            for pw, ph in options:
                if pw <= sw and ph <= sh:
                    placed.append({
                        "x": sx,
                        "y": sy,
                        "width": pw,
                        "height": ph
                    })

                    del free_spaces[i]

                    # right space
                    rw = sw - pw - kerf
                    if rw > 0:
                        free_spaces.append(
                            (sx + pw + kerf, sy, rw, ph)
                        )

                    # bottom space
                    bh = sh - ph - kerf
                    if bh > 0:
                        free_spaces.append(
                            (sx, sy + ph + kerf, sw, bh)
                        )

                    placed_flag = True
                    break

            if placed_flag:
                break

        if not placed_flag:
            remaining.append(part)

    return placed, remaining

# -------------------
# MAIN OPTIMIZER
# -------------------

@app.get("/")
def root():
    return {"status": "SmartCut V2 Running"}

@app.post("/optimize")
def optimize(data: RequestData):

    parts = expand_parts(data.parts)
    parts = sort_parts(parts)

    sheets = []
    remaining = parts

    while remaining:
        placed, remaining = place_on_sheet(
            data.sheet_width,
            data.sheet_height,
            data.kerf,
            remaining
        )

        sheets.append(placed)

    total_sheet_area = (
        data.sheet_width *
        data.sheet_height *
        len(sheets)
    )

    used_area = 0

    for sheet in sheets:
        for p in sheet:
            used_area += p["width"] * p["height"]

    waste = round(
        100 - (used_area / total_sheet_area * 100), 2
    )

    return {
        "sheets_needed": len(sheets),
        "waste_percent": waste,
        "sheets": sheets,
        "message": "SmartCut Engine V2 Active"
    }
