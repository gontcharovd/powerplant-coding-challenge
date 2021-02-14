import json
import pytest
import requests

test_data = [
    (f'example_payloads/payload{i}.json', f'tests/expected/expected{i}.json')
    for i in range(1, 4)
]


@pytest.mark.parametrize('payload_file, expected', test_data)
def test_payload1(payload_file, expected):
    url = 'http://127.0.0.1:8888/productionplan/'
    payload = open(payload_file, 'rb').read()
    expected = open(expected, 'rb').read()
    response = requests.post(url, data=payload)
    assert response.status_code == 200
    assert json.loads(expected) == json.loads(response.json())
