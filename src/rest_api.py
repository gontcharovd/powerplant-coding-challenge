from fastapi import FastAPI
from pydantic import BaseModel, Field
from src.algorithm import MeritOrderCalculation, UnitCommitmentProblem
from typing import List

app = FastAPI()


class Powerplant(BaseModel):
    name: str
    type: str
    efficiency: float
    pmin: int
    pmax: int


class Fuels(BaseModel):
    gas: float = Field(..., alias='gas(euro/MWh)')
    kerosine: float = Field(..., alias='kerosine(euro/MWh)')
    co2: int = Field(..., alias='co2(euro/ton)')
    wind: int = Field(..., alias='wind(%)')


class Payload(BaseModel):
    load: int
    fuels: Fuels
    powerplants: List[Powerplant]


@app.post('/productionplan/')
async def solve_ucp(payload: Payload):
    payload_dict = payload.dict(by_alias=True)
    merit_order = MeritOrderCalculation(payload_dict).calculate()
    ucp = UnitCommitmentProblem(merit_order, payload_dict['load'])
    ucp.solve()
    return ucp.serialize()
