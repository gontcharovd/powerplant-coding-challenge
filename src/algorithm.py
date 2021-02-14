import json

from collections import namedtuple

Unit = namedtuple('Unit', ('name', 'ppm', 'pmin', 'pmax'))


class ProblemInputs:
    """Create the inputs for the Unit Commitment Problem.

    Calculate the Merit Order based on the payload
    """
    def __init__(self, payload):
        self.payload = payload.dict(by_alias=True)
        self.fuels = self.payload['fuels']
        self.load = self.payload['load']
        self.merit_order = self.calculate_merit_order()

    def calculate_ppm(self, plant):
        """Calculate the price per MWh for each plant.

        Kerosene is not a gas: only gas plants were said to emit CO2
        """
        plant_type = plant['type']
        if plant_type == 'windturbine':
            return 0
        elif plant_type == 'gasfired':
            ppm_fuel = self.fuels['gas(euro/MWh)'] / plant['efficiency']
            ppm_co2 = 0.3 * self.fuels['co2(euro/ton)']
            return ppm_fuel + ppm_co2
        elif plant_type == 'turbojet':
            return self.fuels['kerosine(euro/MWh)'] / plant['efficiency']

    def calculate_merit_order(self):
        """Calculate the Merit Order.

        The Merit Order is an ordered list of plants by ppm
        For windturbines pmin = pmax, calculated from the wind(%)
        """
        merit_order = []
        for pp in self.payload['powerplants']:
            ppm = self.calculate_ppm(pp)
            if pp['type'] == 'windturbine':
                pp['pmin'] = pp['pmax'] * self.fuels['wind(%)'] / 100
                pp['pmax'] = pp['pmin']
            merit_order.append(Unit(pp['name'], ppm, pp['pmin'], pp['pmax']))
        merit_order.sort(key=lambda x: x.ppm)
        return merit_order


class UnitCommitmentProblem:
    """Implements the solution to the Unit Commitment Problem. """
    def __init__(self, inputs):
        self.merit_order = inputs.merit_order
        self.load = inputs.load
        self.plant_power = {unit.name: 0.0 for unit in self.merit_order}

    def solve(self):
        """Solve the Unit Commitment Problem.

        The algorithm assigns a power to each unit in the Merit Order (ordered)
        If the power is variable (i.e. not a windturbine), the power assigned
        to the current unit takes into account the pmin of the next unit in
        the Merit Order

        Assumptions that simplify the problem:
            - There exists a unit whose pmin is smaller or equal than the load
            - The load is not greater than the sum of pmax of all units
            - The Merit Order is always respected, i.e. a turbojet will not be
              activated before both gas-fired powerplants are active. This
              assumption is likely too strong. In some cases better solutions
              could be found using recursion with backtracking
        """
        for unit_idx, unit in enumerate(self.merit_order):
            next_unit = None
            if unit_idx < len(self.merit_order) - 1:
                next_unit = self.merit_order[unit_idx + 1]
            if unit.pmin + self.get_total_power() <= self.load:
                if unit.pmin == unit.pmax:
                    self.plant_power[unit.name] = unit.pmin
                else:
                    if unit.pmax + self.get_total_power() >= self.load:
                        power = self.load - self.get_total_power()
                        self.plant_power[unit.name] = power
                    elif next_unit:
                        power = unit.pmax - next_unit.pmin
                        self.plant_power[unit.name] = power
                    else:
                        print('The solution can not be found')

    def get_total_power(self):
        """Calculate the total power of all units.

        Helper function
        """
        total_power = 0
        for power in self.plant_power.values():
            total_power += power
        return total_power

    def serialize(self):
        """Convert the Python dict to the target json format. """
        return json.dumps(
            [{'name': n, 'p': p} for n, p in self.plant_power.items()],
            indent=2
        )
