import csv


def read_from_csv(file):
    output = []
    with open(file+'.csv', newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=' ', quotechar='|')
        for row in reader:
            output.append(row)
    return output


def write_to_csv(msg, file):
    with open(file+'.csv', 'w', newline='') as csvfile:
        spamwriter = csv.writer(csvfile, delimiter=' ',
                                quotechar='|', quoting=csv.QUOTE_MINIMAL)
        spamwriter.writerow(msg)