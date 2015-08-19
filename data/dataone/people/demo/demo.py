""" demo.py

    Demonstration of what the script does with a lot of real documents.

"""

from people import job
import unicodecsv


def main():
    j = job.Job("./documents")
    j.run()
    j.summary()

    print "Writing to CSV"

    # The column headers that are available are varied so we'll process
    # them beforehand to set them up
    saveCollection("demo/people.csv", j.people)
    saveCollection("demo/organizations.csv", j.organizations)


def saveCollection(filename, collection):
    column_names = ["Id"]

    for item in collection:
        for field in item:
            if field not in column_names:
                column_names.append(field)

    column_names = sorted(column_names)

    with open(filename, "wb") as f:
        writer = unicodecsv.writer(f, encoding='utf-8')
        writer.writerow(column_names)

        row_id = 0

        for item in collection:
            row = []
            row.append(str(row_id))

            for column in column_names:
                if column in item:
                    row.append(item[column])
                else:
                    if column != "Id":
                        row.append("")

            writer.writerow(row)

            row_id += 1


if __name__ == "__main__":
    main()
