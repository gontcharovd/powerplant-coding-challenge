# Algorithm

1. Determine MO (merit order)

Payload:
Extract load and fuels
Extract powerplants

Class PowerPlants
For each powerplant get pmin, pmax and PPM (price per MWh, taking efficiency into account)

2. Solve UCP (Unit Commitment Problem)

Naive algorithm:

schedule windmills first because they are free
if too much wind capacity go to next in MO
repeat until MO can fill load gap
if no MO can fill loadgap remove windmill
schedule next in MO:
check if pmin not greater than deficit
schedule until deficit cleared or pmax


# start
power = 0
unit_index = 0
active_units

# base case
power == load: problem solved

# validate: helper function
validate_solution(active_units, p):
if p + sum(power of active_units) smaller than or equal to load:
	return True

# write solver
active_units = list of power plants and their power

if power == load:
  solution found
else:
	for powerplant in range(unit_index:len(units)):
			for p in [pmin:pmax]: possible power (reverse order):
					if validate_soultion(p) is True:
							select this unit and power and unit_index += 1
							call solver again
							(if no p found:) active_units.pop() and unit_index -= 1
