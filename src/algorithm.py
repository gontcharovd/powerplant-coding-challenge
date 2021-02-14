import json
import numpy as np

from collections import namedtuple

Unit = namedtuple('Unit', ('name', 'ppm', 'pmin', 'pmax', 'pfix'))
ActiveUnit = namedtuple('ActiveUnit', ('name', 'power'))


class Inputs:
    """Create a merit order based on a payload. """
    def __init__(self, payload):
        self.payload = payload.dict(by_alias=True)
        self.fuels = self.payload['fuels']
        self.load = self.payload['load']
        self.units = self.create_units()

    def read_payload(self, file):
        with open(file, 'r') as f:
            payload = json.load(f)
            return payload

    def calculate_ppm(self, plant):
        plant_type = plant['type']
        if plant_type == 'windturbine':
            return 0
        elif plant_type == 'gasfired':
            print(self.fuels)
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
        units = []
        for pp in self.payload['powerplants']:
            ppm = self.calculate_ppm(pp)
            pfix = self.get_fixed_power(pp)
            units.append(Unit(pp['name'], ppm, pp['pmin'], pp['pmax'], pfix))
        units.sort(key=lambda x: x.ppm)
        return units


class UnitCommitmentProblem:
    EPSILON = 1e-5
    STEP = 0.1

    def __init__(self, inputs):
        self.units = inputs.units
        self.active_units = []
        self.load = inputs.load
        self.power_sum = 0
        self.unit_start = 0
        self.unit_count = len(self.units)

    def solve(self):
        if np.abs(self.power_sum - self.load) < self.EPSILON:
            return
        else:
            for unit_i in range(self.unit_start, self.unit_count):
                unit = self.units[unit_i]
                for power in self.get_power_values(unit):
                    if self.is_valid_power(power):
                        self.power_sum += power
                        self.unit_start += 1
                        active_unit = ActiveUnit(unit.name, np.round(power, 2))
                        self.active_units.append(active_unit)
                        return self.solve()
                        # backtracking
                        self.unit_start -= 1
                        inactive_unit = self.active_units.pop()
                        self.power_sum -= inactive_unit.power

    def get_power_values(self, unit):
        if unit.pfix is not None:
            return [unit.pfix]
        else:
            return reversed(
                np.arange(unit.pmin, unit.pmax + self.STEP, self.STEP))

    def is_valid_power(self, p):
        return self.power_sum + p <= self.load

    def serialize(self):


if __name__ == '__main__':
    pfile = 'example_payloads/payload3.json'
    inputs = Inputs(pfile)
    print(inputs.units)
    ucp = UnitCommitmentProblem(inputs)
    ucp.solve()
    print(ucp.active_units)
