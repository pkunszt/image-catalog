import argparse
import sys
import elastic
import data
import default_args

store: elastic.Store
reader: elastic.Retrieve
deleter: elastic.Delete
updated: int = 0
deleted: int = 0
total: int = 0


def check(elastic_entry, quiet: bool = True):
    global deleted, updated
    try:
        disk_entry = data.Factory.from_path(elastic_entry.full_path)
    except FileNotFoundError:
        if not quiet:
            print(f"{elastic_entry.full_path} In catalog but not on disk")
        deleter.id(elastic_entry.id)
        deleted += 1
        return

    change = elastic_entry.diff(disk_entry)
    if change:
        store.update(change, elastic_entry.id)
        updated += 1
        if not quiet:
            print(f"Updating {elastic_entry.full_path}")
            print(change)


def main(arg):
    global updated, deleted, store, reader, deleter, total

    parser = argparse.ArgumentParser(
        description="""This tool will sync the catalog with the disk contents. The disk is taken as truth,
    the catalog is changed based on what is on disk.

    New data on disk will NOT be loaded into the catalog, use add_to_catalog for this.
    Items in the catalog that are not on disk anymore are removed from the catalog.
    Items that changed on disk are updated in the catalog (change in size, modify time..)""")
    parser.add_argument('dirname', nargs='?', type=str, help='name of directory to look at')
    parser.add_argument('--quiet', '-q', action='store_true', help='no verbose output')
    default_args.default_arguments(parser)
    args = parser.parse_args(arg)

    connection = elastic.Connection(args.host, args.port)
    if args.index is not None:
        connection.index = args.index

    if not args.quiet:
        print(f"Checking catalog on {connection.host}:{connection.port} with index {connection.index}")

    store = elastic.Store(connection)
    reader = elastic.Retrieve(connection)
    deleter = elastic.Delete(connection)

    updated = deleted = total = 0
    for entry in reader.all_entries(args.dirname):
        check(data.Factory.from_elastic_entry(entry), args.quiet)
        total += 1

    return updated, deleted, total


if __name__ == '__main__':
    main(sys.argv[1:])
    print(f"updated: {updated} entries, deleted {deleted} entries from a total of {total} entries")
