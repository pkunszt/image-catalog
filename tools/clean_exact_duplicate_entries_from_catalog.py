from tools import default_args
import elastic
import argparse


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="""Delete duplicates in the catalog. 
    Duplicates can only happen if the 'allowed duplicates' flag is set when adding items.""")
    parser.add_argument('--dirname', '-d', type=str, help='name of directory check for exact duplicates')
    parser.add_argument('--dryrun', action='store_true', help="don't delete, just print. Default: false")
    default_args.elastic_arguments(parser)
    args = parser.parse_args()

    connection = elastic.Connection(args.host, args.port)
    if args.index is not None:
        connection.index = args.index

    reader = elastic.Retrieve(connection)
    entry_list = dict()
    for entry in reader.all_entries(args.dirname):
        entry_list.setdefault(entry.hash, []).append(entry.meta.id)

    duplicates = [
        item
        for h, items in entry_list.items()
        if len(items) > 1
        for item in items[1:]  # keep first
    ]

    if args.dryrun:
        print(duplicates)
    else:
        deleter = elastic.Delete(connection)
        n = deleter.id_list(duplicates)
        print(f"Deleted {n} duplicates.")
