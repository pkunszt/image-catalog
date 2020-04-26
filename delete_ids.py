import argparse
import os
import csv
import default_args
import elastic


def delete_from_csv(filename):
    with open(filename, "r") as csvfile:
        csv_ids = csv.DictReader(csvfile)
        idlist = [
            line['_id']
            for line in csv_ids
        ]
        deleter.id_list(idlist)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Delete id or list of IDs')
    parser.add_argument('id_or_csvfile', type=str, help='An ID string or a csv file with a list of ID strings')
    default_args.default_arguments(parser)
    args = parser.parse_args()

    connection = elastic.Connection(args.host, args.port)
    if args.index is not None:
        connection.index = args.index
    deleter = elastic.Delete(connection)

    if os.path.isfile(args.id_or_csvfile):
        # delete all IDs from file
        delete_from_csv(args.id_or_csvfile)
    elif os.path.isfile(args.id_or_csvfile + ".csv"):
        # same
        delete_from_csv(args.id_or_csvfile + ".csv")
    else:
        deleter.id(args.id_or_csvfile)
