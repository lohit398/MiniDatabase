import pytest
from minidatabase.SeqScan import SeqScan

def test_seq_scan():
    scan = SeqScan("tests/fixtures/users.csv")
    scan.open()
    rows = []
    while True:
        row = scan.next()
        if len(rows) == 6:
            assert row == None

        if row is None:
            scan.close()
            break
        rows.append(row)
    assert rows == [
        {'name': 'krishna', 'age': None, 'country': 'India'},
        {'name': 'Alice', 'age': '30', 'country': 'US'},
        {'name': 'Bob', 'age': '42', 'country': 'UK'},
        {'name': 'Carol', 'age': '25', 'country': 'US'},
        {'name': None, 'age': '37', 'country': 'France'},
        {'name': 'Alice', 'age': None, 'country': 'India'}
    ]
    assert len(rows) == 6
