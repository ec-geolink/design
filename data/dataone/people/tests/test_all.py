from people import job


def test_same_name_different_email():

    j = job.Job("tests/001_same_name_different_email")
    j.run()

    assert len(j.people) == 2


def test_same_email_different_name():
    j = job.Job("tests/002_same_email_different_name")
    j.run()

    assert len(j.people) == 1
