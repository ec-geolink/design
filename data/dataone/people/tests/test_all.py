from people import job


def test_same_name_different_email():

    j = job.Job("tests/001_same_name_different_email")
    j.run()

    assert len(j.people) == 2


def test_same_email_different_name():
    j = job.Job("tests/002_same_email_different_name")
    j.run()

    assert len(j.people) == 2


def test_can_process_eml_user_id():
    j = job.Job("tests/003_can_process_eml_user_id")
    j.run()

    assert len(j.people) == 1


def test_can_deal_with_middle_names():
    j = job.Job("tests/004_can_deal_with_middle_names")
    j.run()

    assert len(j.people) == 4
