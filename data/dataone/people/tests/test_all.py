import pytest

from people import process as process

def test_same_name_different_email():
    p, o = process.processDirectory("tests/001_same_name_different_email")

    assert len(p) == 2


def test_same_email_different_name():
    p, o = process.processDirectory("tests/002_same_email_different_name")

    assert len(p) == 1
