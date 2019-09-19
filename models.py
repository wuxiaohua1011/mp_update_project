from typing import Dict, List, Optional
from pydantic import BaseModel
from datetime import datetime


class Lattice(BaseModel):
    a: float
    alpha: int
    b: float
    beta: int
    c: float
    gamma: int
    volume: float
    matrix: List[List[int]] = None


class Specie(BaseModel):
    element: str
    occu: float


class Site(BaseModel):
    abc: List[float]
    label: str
    species: List[Specie]
    xyz: List[float]
    properties: Dict[str, int]


class Structure(BaseModel):
    charge: Optional[float] = None
    lattice: Lattice
    sites: List[Site]


class Symmetry(BaseModel):
    source: str
    symbol: str
    number: int
    point_group: str
    crystal_system: str
    hall: str


class BuiltTime(BaseModel):
    string: str

class LastUpdated(BaseModel):
    string: datetime


class CreatedAt(BaseModel):
    string: datetime


class Material(BaseModel):
    chemsys: str
    composition: Dict[str, int] = None
    composition_reduced: Dict[str, int] = None
    created_at: CreatedAt
    density: float
    elements: List[str]
    formula_anonymous: str
    formula_pretty: str
    last_updated: LastUpdated
    nelements: int
    nsites: int
    structure: Structure
    symmetry: Symmetry
    task_id: str
    volume: float
    _built_time: BuiltTime
