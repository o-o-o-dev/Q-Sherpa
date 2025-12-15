import os
from typing import List
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
from zoneinfo import ZoneInfo

from src.equipment_solver import equipment_solver
from src.grouping_solver import grouping_solver
from src.models import (
    Equipment,
    EquipmentAssignment,
    EquipmentRequest,
    GroupingRequest,
    Member,
)
from src.loader import equipments, members

app = FastAPI(title="Q-Sherpa API")

# CORS
origins = [
    "http://localhost",
    "http://127.0.0.1",
]
vercel_origin = os.environ.get("FRONTEND_ORIGIN")
if vercel_origin:
    origins.append(vercel_origin)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {
        "status": "ok",
        "timestamp": datetime.now(ZoneInfo("Asia/Tokyo")),
        "version": "0.1.0",
        "detail": "Kytos Orchestration running",
    }


@app.get("/equipment", response_model=List[Equipment])
def get_equipments():
    return equipments


@app.get("/members", response_model=List[Member])
def get_members():
    return members


@app.post("/grouping", response_model=List[List[Member]])
def grouping(req: GroupingRequest):
    """
    役職などをもとにメンバーを班に分ける
    """
    return grouping_solver(req.members, req.num_teams, req.settings)


@app.post("/equipment", response_model=List[EquipmentAssignment])
def equipment(req: EquipmentRequest):
    """
    班分けを考慮して装備を割り当てる
    """
    return equipment_solver(req.teams, req.equipments, req.settings)
