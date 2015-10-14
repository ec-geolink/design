""" checks.py
    Bryce Mecum (mecum@nceas.ucsb.edu)

    Methods used for checking facts about two entities.
"""


def fieldsSame(first, second, fields):
    """ Checks if all `fields` of `first` are the same as in `second`"""

    for field in fields:
        if field not in first or field not in second:
            return False

        if first[field] != second[field]:
            return False

    return True


def fieldsDifferent(first, second, fields):
    """ Checks if all `fields` of `first` are different than `second`"""

    for field in fields:
        if field in first and field in second:
            if first[field] == second[field]:
                return False

    return True


def fieldsNotDifferent(first, second, fields):
    """ Checks if `fields` are not different between `first` and `second`

        Allows for the possibility of the field not existing. For example,
        if a user doesn't have a middle name in one record but does in another
        andd their first and last name are the same in both records, we'd like
        to let a rule matching first+middle+last not fail.
    """

    for field in fields:
        if field in first and field in second:
            if first[field] != second[field]:
                return False

    return True
