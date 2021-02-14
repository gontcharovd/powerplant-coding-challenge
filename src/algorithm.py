import json
import numpy as np
import sys

from collections import namedtuple

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
    STEP = 0.1

    def __init__(self, inputs):
        self.merit_order = inputs.merit_order
        self.active_units = []
        self.load = inputs.load
        self.power_sum = 0
        self.unit_start = 0
        self.plant_count = len(self.merit_order)

    def solve(self):
        # base case
        if np.abs(self.power_sum - self.load) < self.EPSILON:
            # add remaining inactive units with power p=0
            for unit in self.merit_order:
                if unit.name not in [u['name'] for u in self.active_units]:
                    inactive_unit = {
                        'name': unit.name,
                        'p': 0
                    }
                    self.active_units.append(inactive_unit)
            return
        else:
            # not allowed to have state!
            for unit_i in range(self.unit_start, self.plant_count):
                unit = self.merit_order[unit_i]
                for power in self.get_power_values(unit):
                    if self.is_valid_power(power):
                        self.power_sum += power
                        self.unit_start += 1
                        active_unit = {
                            'name': unit.name,
                            'p': np.round(power, 2)
                        }
                        self.active_units.append(active_unit)
                        return self.solve()
                        # backtracking
                        self.unit_start -= 1
                        inactive_unit = self.active_units.pop()
                        self.power_sum -= inactive_unit['p']

    def get_power_values(self, unit):
        if unit.pfix is not None:
            return [unit.pfix]
        else:
            return reversed(
                np.arange(unit.pmin, unit.pmax + self.STEP, self.STEP))

    def is_valid_power(self, p):
        return self.power_sum + p <= self.load

    def serialize(self):
        return json.dumps(self.active_units, indent=2)


if __name__ == '__main__':
    payload = 'example_payloads/payload2.json'
    inputs = ProblemInputs(payload)
    ucp = UnitCommitmentProblem(inputs)
    ucp.solve()
    print(ucp.serialize())
