""" dump.py

    Demonstration of what the script does with a lot of real documents.

"""

from people import job


def main():
    j = job.Job("/Users/mecum/src/d1dump/documents-random")
    j.run()
    j.finish()


if __name__ == "__main__":
    main()
