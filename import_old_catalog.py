import json
import os
import pathlib
import shutil
import sys
import re
import argparse
import elastic
import data
import default_args
import constants


def walk_year(directory_name: str, dest_path: str):
    months = constants.get_months()
    count = 0
    with os.scandir(directory_name) as iterator:
        for item in iterator:
            if item.is_dir():
                if item.name in months:
                    count += catalog_month(item.path, os.path.join(dest_path, item.name))
                else:
                    count += catalog_as_is(item.path, os.path.join(dest_path, item.name))

    return count


def catalog_month(month_directory: str, dest_path: str):
    count = 0
    with os.scandir(month_directory) as iterator:
        for item in iterator:
            if item.is_dir():
                count += catalog_as_is(item.path, os.path.join(dest_path, item.name))

    return count + read_and_store_directory(month_directory, dest_path)


def catalog_as_is(directory: str, dest_path: str):
    count = 0
    if directory in ignored_dirs:
        return 0
    with os.scandir(directory) as iterator:
        for item in iterator:
            if item.is_dir():
                count += catalog_as_is(item.path, os.path.join(dest_path, item.name))

    return count + read_and_store_directory(directory, dest_path, keep_names=True)


def read_and_store_directory(directory, dest_path, keep_names=False):
    folder.read(directory)
    folder.drop_duplicates()
    stored = store.list(folder.files, destination_folder=dest_path, name_from_captured_date=True,
                        keep_manual_names=keep_names)
    copy_to_catalog(stored)
    print(f"Added from {directory} : {len(stored)}")
    return len(stored)


def copy_to_catalog(stored_items):
    for item in stored_items:
        source = item['original_path']
        dest_path = os.path.join(dest_root, item['path'])
        dest = os.path.join(dest_path, item['name'])
        if not os.path.exists(dest_path):
            pathlib.Path(dest_path).mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, dest)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="""Import old catalog into new one. 
    The directory structure has meaning here. The data will be taken from the old structure down. 
    Starting from a YEAR we will traverse into the given months and subdirs are kept as such.
    Duplicates in the same dir are not stored, but duplicates in named directories outside of month are.""")
    parser.add_argument('basedir', type=str, help='Base directory of old catalog.')
    parser.add_argument('year', type=str, help='Year to import.')
    parser.add_argument('--catalog_root', type=str, help='Use this as catalog root')
    default_args.default_arguments(parser)
    args = parser.parse_args()

    year = re.compile("[1-2]\d\d\d")
    if not year.match(args.year):
        print("Year needs to be a 4 digit number")
        sys.exit(-1)

    import_path = os.path.join(args.basedir, args.year)
    if not os.path.isdir(import_path):
        print(f"Invalid directory {import_path}")
        sys.exit(-1)

    with open("config.json", 'r') as file:
        config = json.load(file)
    dest_root = config['nas_root']
    if args.catalog_root:
        dest_root = args.catalog_root

    ignored_dirs = ["_gsdata_"]
    connection = elastic.Connection(args.host, args.port)
    if args.index:
        connection.index = args.index
    store = elastic.Store(connection)

    folder = data.Folder()
    c = walk_year(import_path, args.year)

    print(f"Added {c} entries to catalog.")
