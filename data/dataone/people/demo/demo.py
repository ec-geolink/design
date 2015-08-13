""" demo.py

    Demonstration of what the script does with a lot of real documents.

"""

from people import processing

def main():
    people,organizations = processing.processDirectory("./documents")

    print "All %d People..." % len(people)

    for person in people:
        print processing.personString(person)

    print "All %d Organizations..." % len(organizations)

    for organization in organizations:
        print processing.organizationString(organization)

if __name__ == "__main__":
    main()
