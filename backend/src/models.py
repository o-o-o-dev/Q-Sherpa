from enum import Enum
from typing import List, Dict, Optional
from pydantic import BaseModel, TypeAdapter


class RoleFixed(Enum):
    Equipment = "equipment"
    Weather = "weather"
    Meal = "meal"


class RoleAuthoritative(Enum):
    SL = "SL"
    CL = "CL"


class Carrier(Enum):
    Docomo = "docomo"
    Au = "au"
    Softbank = "softbank"
    Rakuten = "rakuten"


class Member(BaseModel):
    id: int
    name: str
    grade: int
    gender: str
    role_fixed: Optional[RoleFixed] = None
    role_authoritative: Optional[RoleAuthoritative] = None
    driver: bool
    carrier: Optional[Carrier] = None
    exp_years: float


MemberList = TypeAdapter(List[Member])


class Equipment(BaseModel):
    id: int
    name: str
    weight: float
    capacity: Optional[float] = None


EquipmentList = TypeAdapter(List[Equipment])


class GroupingSettings(BaseModel):
    num_reads: int = 1000
    groupSizeWeight: float = 1.0
    gradePopulationWeight: float = 1.0
    genderShouldBeZeroWeight: float = 1.0
    genderPairBonusWeight: float = 1.0
    rolePopulationWeight: float = 2.0
    driverPopulationWeight: float = 1.5
    carrierPopulationWeight: float = 0.3
    interTeamExperienceSimilarityWeight: float = 0.5
    intraTeamExperienceSimilarityWeight: float = 0.5


class EquipmentSettings(BaseModel):
    num_reads: int = 100
    P: float = 0.5
    weightWeight: float = 1.0


class GroupingRequest(BaseModel):
    members: List[Member]
    num_teams: int
    settings: GroupingSettings


class EquipmentRequest(BaseModel):
    teams: List[List[Member]]
    equipments: List[Equipment]
    settings: EquipmentSettings = EquipmentSettings()


class EquipmentAssignment(BaseModel):
    member: Member
    equipment: List[Equipment]


class PackingResult(BaseModel):
    items: List[int]
    total_weight: float
    load_ratio: float


class TeamResult(BaseModel):
    members: Dict[int, PackingResult]
    safety_score: float


class OptimizeResponse(BaseModel):
    teams: List[TeamResult]
    energy: float
