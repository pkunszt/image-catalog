import default_args
import elastic
import argparse


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="""Delete duplicates in the same directory. 
    You need to provide the directory to find duplicates in. This will be based on the catalog entries
    and not on what is actually on disk, make sure you add everything to the catalog and sync with it
    before running this so that it will execute correctly. It is assumed that 
    The file name with the name that makes most sense is kept. If one of the names""")
    parser.add_argument('--dirname', '-d', type=str, help='name of directory check for exact duplicates')
    parser.add_argument('--dryrun', action='store_true', help="don't delete, just print. Default: false")
    default_args.default_arguments(parser)
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
