import pytest
from minidatabase.SeqScan import SeqScan

def test_seq_scan():
    scan = SeqScan("tests/fixtures/users.csv")
    rows = []
    while True:
        row = scan.next()
        if(row == None):
            assert row == None
            scan.close()
            break
        rows.append(row)
    assert rows == [{
        'name':'Alice',
        'age':'30',
        'country':'US'
    },{
        'name':'Bob',
        'age':'42',
        'country':'UK'
    },{
        'name':'Carol',
        'age':'25',
        'country':'US'
    },{
        'name':'null',
        'age':'25',
        'country':'France'
    },{
        'name':None,
        'age':'25',
        'country':'India'
    }]
    assert len(rows) == 5

        
