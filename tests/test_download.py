import os
import download

WHERE = os.path.dirname(__file__)

def test_list_packages():
    found = download.list_packages(None, WHERE)
    assert found
    assert len(found) == 5
    assert found[0].startswith("https://conda.anaconda.org")


def test_list_packages_all_strict():
    found = download.list_packages(None, WHERE, allvariants=True)
    assert found
    assert len(found) == 9
    assert found[0].startswith("https://conda.anaconda.org")


def test_list_packages_all_large():
    found = download.list_packages(None, WHERE, allvariants=True, acceptallorigins=True)
    assert found
    assert len(found) == 17
    assert found[0].startswith("https://conda.anaconda.org")
