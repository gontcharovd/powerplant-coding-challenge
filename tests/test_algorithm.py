from src.algorithm import Inputs, UnitCommitmentProblem, ActiveUnit


def test_payload1():
    inputs = Inputs('example_payloads/payload1.json')
    ucp = UnitCommitmentProblem(inputs)
    ucp.solve()
    solution = [
        ActiveUnit('windpark1', 90),
        ActiveUnit('windpark2', 21.6),
        ActiveUnit('gasfiredbig1', 368.4)
    ]
    assert all([u == s for u, s in zip(ucp.active_units, solution)])


def test_payload3():
    inputs = Inputs('example_payloads/payload3.json')
    ucp = UnitCommitmentProblem(inputs)
    ucp.solve()
    solution = [
        ActiveUnit('windpark1', 90),
        ActiveUnit('windpark2', 21.6),
        ActiveUnit('gasfiredbig1', 460),
        ActiveUnit('gasfiredbig2', 338.4)
    ]
    assert all([u == s for u, s in zip(ucp.active_units, solution)])
