import argparse
import sys
import elastic
import data
import default_args
import os
import json
from data import Factory

store: elastic.Store
reader: elastic.Retrieve
deleter: elastic.Delete
updated: int = 0
deleted: int = 0
total: int = 0
nas_root: str = ""
in_catalog_only: list = []
in_catalog_only_checksums: dict = dict()
elastic_paths: set = set()
on_disk_only: list = []


def check_catalog(elastic_entry):
    global deleted, updated
    path = os.path.join(nas_root, elastic_entry.full_path)
    if not os.path.isfile(path):
        print(f"In Catalog but not on disk: {elastic_entry.full_path}")
        in_catalog_only.append(elastic_entry)
        in_catalog_only_checksums[elastic_entry.checksum] = path
    else:
        elastic_paths.add(path)


def check_files(dirname):
    with os.scandir(dirname) as iterator:
        for item in iterator:
            if item.is_dir():
                check_files(item.path)
            elif item.is_file():
                if item.path not in elastic_paths:
                    print(f"File {item.path} is on disk but not in elastic")
                    on_disk_only.append(Factory.from_path(item.path))


def main(arg):
    global updated, deleted, store, reader, deleter, total, nas_root

    parser = argparse.ArgumentParser(
        description="""This tool will sync the catalog with the disk contents. The disk is taken as truth,
    the catalog is changed based on what is on disk.

    New data on disk will be loaded into the catalog.
    Items in the catalog that are not on disk anymore are removed from the catalog, if they were moved,
    that will be detected. Items that changed on disk with the same name are not detected.
    (change in size, modify time..)""")
    parser.add_argument('dirname', nargs='?', type=str, help='name of directory to look at')
    parser.add_argument('--quiet', '-q', action='store_true', help='no verbose output')
    parser.add_argument('--nas_root', type=str, help='Use this as catalog root on NAS')
    parser.add_argument('--dropbox_root', type=str, help='Use this as catalog root on Dropbox')
    default_args.default_arguments(parser)
    args = parser.parse_args(arg)

    connection = elastic.Connection(args.host, args.port)
    if args.index is not None:
        connection.index = args.index

    with open("config.json", 'r') as file:
        config = json.load(file)
    nas_root = config['nas_root'] if not args.nas_root else args.nas_root

    if not args.quiet:
        print(f"Checking catalog on {connection.host}:{connection.port} with index {connection.index}")

    store = elastic.Store(connection)
    reader = elastic.Retrieve(connection)
    deleter = elastic.Delete(connection)

    updated = deleted = total = 0
    for entry in reader.all_entries(args.dirname):
        check_catalog(data.Factory.from_elastic_entry(entry))

    check_files(nas_root)
    if not args.quiet:
        print(f"Catalog entries in sync: {len(elastic_paths)}")
        print(f"Catalog entries not found on disk: {len(in_catalog_only.keys())}")
        print(f"On disk but not on catalog: {len(on_disk_only)}")
    elastic_paths.clear()

    # detected moved file
    for new_file in on_disk_only:
        if new_file.checksum in in_catalog_only_checksums.keys():
            cat_item = in_catalog_only_checksums[new_file.checksum]
            print(f"File {cat_item} moved to {new_file.full_path}")
            # TODO update catalog entry to point to new location, deal with more than one item in list
            updated += 1
        else:
            print(f"File {new_file.full_path} is only on disk but not in Catalog")
            # TODO load this item into the catalog
            deleted += 1

    for file in in_catalog_only:
        print(f"""{file.full_path} is only in the catalog, was probably removed manually. Remove from catalog and also 
        remove remote copies or restore from dropbox if possible?""")
        # TODO ask for input and delete catalog entry, remove also dropbox if any, deal with more than one item in list
        for item in reader.get_by_checksum(file.checksum):
            if item.id != file.id:
                print(f"{file.full_path} is still in catalog as {item.full_path}")

    return


if __name__ == '__main__':
    main(sys.argv[1:])
    print(f"updated: {updated} entries, deleted {deleted} entries in catalog")
