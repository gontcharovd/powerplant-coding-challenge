import json
import pytest
import requests

from src.algorithm import UnitCommitmentProblem, Unit

test_data = [
    (f'example_payloads/payload{i}.json', f'tests/expected/expected{i}.json')
    for i in range(1, 4)
]


@pytest.mark.parametrize('payload_file, expected', test_data)
def test_example_payloads(payload_file, expected):
    """Test if the UCP is correctly solved for the three given payloads. """
    url = 'http://127.0.0.1:8888/productionplan/'
    payload = open(payload_file, 'rb').read()
    expected = open(expected, 'rb').read()
    response = requests.post(url, data=payload)
    assert response.status_code == 200
    assert json.loads(expected) == json.loads(response.json())
    print(response.json())
