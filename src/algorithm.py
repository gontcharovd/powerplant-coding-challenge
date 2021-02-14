import json
import numpy as np
import sys

from collections import namedtuple

sys.setrecursionlimit(100000)
Unit = namedtuple('Unit', ('name', 'ppm', 'pmin', 'pmax', 'pfix'))


class ProblemInputs:
    """Create a merit order based on a payload. """
    def __init__(self, payload):
        # self.payload = payload.dict(by_alias=True)
        self.payload = self.read_payload(payload)
        self.fuels = self.payload['fuels']
        self.load = self.payload['load']
        self.merit_order = self.create_units()

    def read_payload(self, file):
        with open(file, 'r') as f:
            payload = json.load(f)
            return payload

    def calculate_ppm(self, plant):
        plant_type = plant['type']
        if plant_type == 'windturbine':
            return 0
        elif plant_type == 'gasfired':
            ppm_fuel = self.fuels['gas(euro/MWh)'] / plant['efficiency']
            ppm_co2 = 0.3 * self.fuels['co2(euro/ton)']
            return ppm_fuel + ppm_co2
        elif plant_type == 'turbojet':
            # Kerosene is not a gas but a liquid
            # Only gas plants were said to emit CO2
            return self.fuels['kerosine(euro/MWh)'] / plant['efficiency']

    def get_fixed_power(self, plant):
        if plant['type'] == 'windturbine':
            return plant['pmax'] * self.fuels['wind(%)'] / 100
        else:
            return None

    def create_units(self):
        merit_order = []
        for pp in self.payload['powerplants']:
            ppm = self.calculate_ppm(pp)
            pfix = self.get_fixed_power(pp)
            merit_order.append(Unit(pp['name'], ppm, pp['pmin'], pp['pmax'], pfix))
        merit_order.sort(key=lambda x: x.ppm)
        return merit_order


class UnitCommitmentProblem:
    EPSILON = 1e-5
    STEP = 1

    def __init__(self, inputs):
        self.merit_order = inputs.merit_order
        self.load = inputs.load
        self.plant_power = {unit.name: 0.0 for unit in self.merit_order}

    def solve(self):
        if np.abs(self.get_total_power() - self.load) < self.EPSILON:
            print(self.plant_power)
            input("More")
        else:
            for unit in self.merit_order:
                if self.plant_power[unit.name] == 0.0:
                    for power in self.get_power_values(unit):
                        if power > 0 and self.is_valid_power(power):
                            self.plant_power[unit.name] = power
                            self.solve()
                            self.plant_power[unit.name] = 0.0

    def get_power_values(self, unit):
        if unit.pfix is not None:
            return [unit.pfix]
        else:
            return reversed(
                np.arange(unit.pmin, unit.pmax + self.STEP, self.STEP))

    def get_total_power(self):
        total_power = 0
        for power in self.plant_power.values():
            total_power += power
        return total_power

    def is_valid_power(self, power):
        return self.get_total_power() + power <= self.load

    def serialize(self):
        return json.dumps(self.plant_power, indent=2)


if __name__ == '__main__':
    payload = 'example_payloads/payload2.json'
    inputs = ProblemInputs(payload)
    ucp = UnitCommitmentProblem(inputs)
    # print(ucp.plant_power)
    # print(ucp.merit_order)
    ucp.solve()
    # print(ucp.serialize())
