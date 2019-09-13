from typing import Dict, List, Any
from pydantic import BaseModel


class CreatedAt(BaseModel):
    string: str


class LastUpdated(BaseModel):
    string: str


class Lattice(BaseModel):
    a: float
    alpha: int
    b: float
    beta: int
    c: float
    gamma: int
    volume: float
    matrix: List[List[int]] = None


class Specy(BaseModel):
    element: str
    occu: int


class Site(BaseModel):
    abc: List[float]
    label: str
    species: List[Specy]
    xyz: List[float]
    properties: Dict[str, int]


class Structure(BaseModel):
    charge: Any
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


class ID(BaseModel):
    oid: str


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
    _id: ID
