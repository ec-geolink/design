""" demo.py

    Demonstration of what the script does with a lot of real documents.

"""

from people import job


def main():
    j = job.Job("./documents")
    j.run()
    j.summary()

if __name__ == "__main__":
    main()
