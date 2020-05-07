import argparse
import sys
import elastic
import data
import default_args
import os
import json

from catalog import Constants
from my_decorators import run_time
from data import Factory

store: elastic.Store
reader: elastic.Retrieve
deleter: elastic.Delete
updated: int = 0
deleted: int = 0
loaded: int = 0
total: int = 0
recursive: bool = False
nas_root: str = ""
in_catalog_only: list = []
in_catalog_only_checksums: set = set()
elastic_paths: set = set()
on_disk_only: list = []
updated_checksums: set = set()


@run_time
def check_files_in_catalog(dirname: str):
    for entry in reader.all_entries(dirname):
        check_catalog(data.Factory.from_elastic_entry(entry))


def check_catalog(elastic_entry):
    global deleted, updated
    path = os.path.join(nas_root, elastic_entry.full_path)
    if not os.path.isfile(path):
        # print(f"In Catalog but not on disk: {elastic_entry.full_path}")
        in_catalog_only.append(elastic_entry)
        in_catalog_only_checksums.add(elastic_entry.checksum)
    else:
        elastic_paths.add(path)


@run_time
def check_files_on_disk(dirname: str):
    check_files(dirname)


def check_files(dirname: str):
    with os.scandir(dirname) as iterator:
        for item in iterator:
            if item.name in Constants.ignored_paths:
                continue
            if item.is_dir() and recursive:
                check_files(item.path)
            elif item.is_file():
                if item.path not in elastic_paths and relaxed_encoding_compares_false(item.path, elastic_paths):
                    # print(f"File {item.path} is on disk but not in elastic")
                    on_disk_only.append(Factory.from_path(item.path))


def relaxed_encoding_compares_false(path: str, paths: set) -> bool:
    arr_path = path.encode()
    diaeresis = arr_path.find(b"\xcc\x88")
    if diaeresis > 0:
        if arr_path[diaeresis - 1] == ord('u'):
            arr_path = arr_path.replace(b"u\xcc\x88", b"\xc3\xbc")
        elif arr_path[diaeresis - 1] == ord('a'):
            arr_path = arr_path.replace(b"a\xcc\x88", b"\xc3\xa4")
        elif arr_path[diaeresis - 1] == ord('o'):
            arr_path = arr_path.replace(b"o\xcc\x88", b"\xc3\xb6")

    # acute = arr_path.find(b"\xcc\x81")
    # if acute > 0:
    #     if arr_path[diaeresis - 1] == ord('u'):
    #         arr_path = arr_path.replace(b"u\xcc\x81", b"\xc3\xba")
    #     elif arr_path[diaeresis - 1] == ord('a'):
    #         arr_path = arr_path.replace(b"a\xcc\x81", b"\xc3\xa1")
    #     elif arr_path[diaeresis - 1] == ord('o'):
    #         arr_path = arr_path.replace(b"o\xcc\x81", b"\xc3\xb3")
    #     elif arr_path[diaeresis - 1] == ord('e'):
    #         arr_path = arr_path.replace(b"e\xcc\x81", b"\xc3\xa9")

    return not arr_path.decode() in paths


def main(arg):
    global updated, deleted, loaded, store, reader, deleter, total, nas_root, recursive

    parser = argparse.ArgumentParser(
        description="""This tool will sync the catalog with the disk contents. The disk is taken as truth,
    the catalog is changed based on what is on disk.

    New data on disk will be loaded into the catalog.
    Items in the catalog that are not on disk anymore are removed from the catalog, if they were moved,
    that will be detected. Items that changed on disk with the same name are not detected.
    (change in size, modify time..)""")
    parser.add_argument('dirname', type=str, help='name of directory to look at')
    parser.add_argument('--quiet', '-q', action='store_true', help='no verbose output')
    parser.add_argument('--recursive', '-r', action='store_true', help='no verbose output')
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

    recursive = args.recursive
    if not args.quiet:
        print(f"Checking catalog on {connection.host}:{connection.port} with index {connection.index}")

    store = elastic.Store(connection)
    reader = elastic.Retrieve(connection)
    deleter = elastic.Delete(connection)

    updated = deleted = total = loaded = 0

    check_files_in_catalog(args.dirname)
    check_files_on_disk(os.path.join(nas_root, args.dirname))
    if not args.quiet:
        print(f"Catalog entries in sync: {len(elastic_paths)}")
        print(f"Catalog entries not found on disk: {len(in_catalog_only)}")
        print(f"On disk but not on catalog: {len(on_disk_only)}")
    elastic_paths.clear()

    # detected moved file or deleted duplicate
    store_list = []
    updated_checksums.clear()
    for new_file in on_disk_only:
        if new_file.checksum in in_catalog_only_checksums:
            for cat_item in reader.get_by_checksum(new_file.checksum):
                update_catalog_entry_for_moved_file(cat_item, new_file)
                break
        else:
            found = False
            for item in reader.get_by_checksum(new_file.checksum):
                if not os.path.exists(os.path.join(nas_root, item.full_path)):
                    update_catalog_entry_for_moved_file(item, new_file)
                    found = True
                    break
            if not found:
                print(f"File {new_file.full_path} is only on disk but not in Catalog")
                yes = input("Load into catalog y/n?")
                if yes.lower().startswith('y'):
                    new_file.path = new_file.path[len(nas_root) + 1:]
                    store_list.append(new_file)
                    loaded += 1

    if len(store_list) > 0:
        store.list(item for item in store_list)

    for file in in_catalog_only:
        if file.checksum in updated_checksums:
            continue
        print(f"""{file.full_path} is only in the catalog.""")
        skip = False
        for item in reader.get_by_checksum(file.checksum):
            if item.id != file.id:
                print(f"{file.full_path} is still in catalog as {item.full_path}. Deleting this duplicate.")
                deleter.id(file.id)
                deleted += 1
                skip = True
                break
        if skip:
            continue
        yes = input('Delete this file from catalog y/n?:')
        if yes.lower().startswith('y'):
            deleter.id(file.id)
            deleted += 1

    return


def update_catalog_entry_for_moved_file(cat_item, new_file):
    global updated, store, nas_root, updated_checksums
    new_file.path = new_file.path[len(nas_root) + 1:]
    print(f"File {cat_item.full_path} moved to {new_file.full_path}")
    store.update(cat_item.diff(new_file), cat_item.id)
    updated_checksums.add(new_file.checksum)
    updated += 1


if __name__ == '__main__':
    main(sys.argv[1:])
    print(f"updated: {updated} entries, deleted {deleted} entries and loaded {loaded} entries in catalog")
