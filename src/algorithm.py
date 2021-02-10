import json
from collections import namedtuple

Unit = namedtuple('Unit', ('name', 'pmin', 'pmax', 'ppm', 'fixed_power'))


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
            return self.fuels['kerosine(euro/MWh)'] / plant['efficiency']

    def calculate_power(self, plant):
        if plant['type'] == 'windturbine':
            return plant['pmax'] * self.fuels['wind(%)'] / 100
        else:
            return None

    def create_units(self):
        for pp in self.payload['powerplants']:
            ppm = self.calculate_ppm(pp)
            fixed_power = self.calculate_power(pp)
            yield Unit(pp['name'], pp['pmin'], pp['pmax'], ppm, fixed_power)


class UnitCommitmentProblem:
    def __init__(self, inputs):
        self.units = inputs.units
        self.target_load = inputs.target_load
        self.power = 0


if __name__ == '__main__':
    pfile = 'example_payloads/payload1.json'
    inputs = Inputs(pfile)
    ucp = UnitCommitmentProblem(inputs)
    print(list(ucp.units))
    print(ucp.target_load)
