# Algorithm

1. Determine MO (merit order)

Payload:
Extract load and fuels
Extract powerplants

Class PowerPlants
For each powerplant get pmin, pmax and PPM (price per MWh, taking efficiency into account)

2. Solve UCP (Unit Commitment Problem)

Naive algorithm:

1. schedule windmills first because they are free
2. schedule next in MO:
	* check if pmin not greater than deficit
	* schedule until deficit cleared or pmax


