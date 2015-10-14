"""
"""

import re


class Validator():
    """
    """

    def __init__(self):
        # Rules that, if matched, reject the record

        """
        Set up organization name patterns first because they are re-used for
        people['organization'] and organization['name']
        """

        org_patterns = {
             'working_groups':  re.compile("NCEAS:?\s*\d+"),
             'just_numbers':    re.compile("^\d*$"),
             'junk_names':      re.compile("^[a-z]{3,4}\s*\d*$"),
             'no_letters':      re.compile("^[^a-zA-Z\u0000-\u007F]+$"),
             'journal_article': re.compile("\d+:\d+-\d+")
         }


        """
        Rules are represented as a set of nested dictionaries.
        The rules follow a hierarchy like this:

            rules
                record type (e.g. person|organization)
                    field name (e.g. full_name)
                        rule (one of actions|min_length|strings|patterns)

        Each field has an action rule that specifies whether to blank the field
        if it matches the rule or to invalidate the entire record.

        When a record fails to validate, None is returned.
        Otherwise, the original record is returned with possibly fewer fields
        """

        self.rules = {
            'person' : {
                'full_name' : {
                    'action' : 'invalidate',
                    'min_length' : 1,
                    'strings' : ['test', 'read', 'test1', 'test 2', 'asdf',
                                 'adfs', 'test test', 'tret trert', 'GAA',
                                 'BBB', 'tetqe', 'GGGG', 'You and your mentor']

                },
                'organization' : {
                    'action' : 'delete',
                    'patterns' : org_patterns
                }
            },
            'organization' : {
                'name' : {
                    'action' : 'invalidate',
                    'min_length' : 1,
                    'strings' : [ "Select state or territory here.", "null", "test"],
                    'patterns' : org_patterns
                }
            }
        }


    def runRules(self, value, rules):
        """
        Run a set of rules for the provided value.
        """

        """
        Never validate unicode values.

        Throwing this unicode error checks whether the string is unicode or
        not. I'm not sure how robust this method is but it works AFAIK
        """

        try:
            bytes(value)
        except UnicodeEncodeError:
            return True


        # Run individual rule types
        if 'min_length' in rules:
            if len(value) < rules['min_length']:
                return False

        if 'strings' in rules:
            for string_rule in rules['strings']:
                if value == string_rule:
                    return False

        if 'patterns' in rules:
            for pattern in rules['patterns']:
                if rules['patterns'][pattern].search(value):
                    return False

        return True


    def validate(self, record):
        """
        Validate the provided record with any rules that have been established
        for its type.

        By default, all records are considered valid until proven otherwise.
        """

        if record is None:
            return None

        if 'type' not in record:
            raise Exception("Record had no type: %s." % record)

        is_valid = True

        record_type = record['type']
        rules = self.rules[record_type]

        for field in rules:
            if field not in record:
                continue

            field_rules = rules[field]
            is_valid = self.runRules(record[field], field_rules)

            if not is_valid:
                if 'action' in field_rules:
                    if field_rules['action'] == 'invalidate':
                        is_valid = False
                    elif field_rules['action'] == 'delete':
                        del record[field]


        if not is_valid:
            record = None

        return record



if __name__ == "__main__":
    test_records = [
        {
            'type':'person',
            'full_name':'Bryce'
        },
        {
            'type':'person',
        },
        {
            'type':'organization',
        },
        {
            'type':'person',
            'full_name':'GGGG'
        },
        {
            'type':'person',
            'full_name':'Some Person',
            'organization':'NCEAS: 50020 This is a working group org.'
        },
        {
            'type':'person',
            'full_name':'You and your mentor'
        },
        {
            'type':'organization',
            'name':''
        },
        {
            'type':'organization',
            'name':'NCEAS: 50020 This is a working group org.'
        }
    ]

    v = Validator()

    for r in test_records:
        print "IN : %s" % r
        result = v.validate(r)
        print "OUT: %s" % result
        print ""
