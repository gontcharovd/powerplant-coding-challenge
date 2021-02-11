import json
from collections import namedtuple

Unit = namedtuple('Unit', ('name', 'ppm', 'power_values'))
# possible power values instead of fixed_power


class Inputs:
    """Create a merit order based on a payload. """
    def __init__(self, payload_file):
        self.payload = self.read_payload(payload_file)
        self.fuels = self.payload['fuels']
        self.target_load = self.payload['load']
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
            ppm_fuel = self.fuels['gas(euro/MWh)'] / plant['efficiency']
            ppm_co2 = 0.3 * self.fuels['co2(euro/ton)']
            return ppm_fuel + ppm_co2
        elif plant_type == 'turbojet':
            # Kerosene is not a gas but a liquid
            # Only gas plants were said to emit CO2
            return self.fuels['kerosine(euro/MWh)'] / plant['efficiency']

    def calculate_power_values(self, plant):
        if plant['type'] == 'windturbine':
            return plant['pmax'] * self.fuels['wind(%)'] / 100
        else:
            return [p for p in range(int(plant['pmin']), int(plant['pmax']) + 1)]

    def create_units(self):
        for powerplant in self.payload['powerplants']:
            ppm = self.calculate_ppm(powerplant)
            power_values = self.calculate_power_values(powerplant)
            yield Unit(powerplant['name'], ppm, power_values)


ActiveUnit = namedtuple('ActiveUnit', ('name', 'power'))


class UnitCommitmentProblem:
    def __init__(self, inputs):
        self.units = list(inputs.units)
        self.target_load = inputs.target_load
        self.power = 0

    def sort_units(self):
        self.units.sort(key=lambda x: x.ppm)



if __name__ == '__main__':
    pfile = 'example_payloads/payload1.json'
    inputs = Inputs(pfile)
    ucp = UnitCommitmentProblem(inputs)
    print(list(ucp.units))
    ucp.sort_units()
    print(list(ucp.units))
