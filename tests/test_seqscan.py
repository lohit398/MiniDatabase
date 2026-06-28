import pytest
from minidatabase.SeqScan import SeqScan

def test_seq_scan():
    scan = SeqScan("tests/fixtures/users.csv")
    rows = []
    while True:
        row = scan.next()
        if(row == None):
            scan.close()
            break
        rows.append(row)
    assert rows[0] == {
        'name':'Alice',
        'age':'30',
        'country':'US'
    }
    assert rows[3] == {
        'name':'null',
        'age':'25',
        'country':'France'
    }
    assert len(rows) == 4

        
