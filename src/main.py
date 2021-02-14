from fastapi import FastAPI
from pydantic import BaseModel, Field
from src.algorithm import ProblemInputs, UnitCommitmentProblem
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
    inputs = ProblemInputs(payload)
    ucp = UnitCommitmentProblem(inputs)
    ucp.solve()
    return inputs.merit_order, ucp.serialize()
