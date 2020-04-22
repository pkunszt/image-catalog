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
from data import DBox


def walk_year(directory_name: str, dest_path: str) -> int:
    months = constants.get_months()
    count = 0
    with os.scandir(directory_name) as iterator:
        for item in iterator:
            if item.is_dir():
                if item.name in months:
                    count += catalog_dir(item.path, os.path.join(dest_path, item.name), keep_names=False)
                else:
                    count += catalog_dir(item.path, os.path.join(dest_path, item.name))

    return count


def catalog_dir(directory: str, dest_path: str, keep_names: bool = True) -> int:
    count = 0
    if directory in ignored_dirs:
        return 0
    with os.scandir(directory) as iterator:
        for item in iterator:
            if item.is_dir():
                count += catalog_dir(item.path, os.path.join(dest_path, item.name))

    return read_and_store_directory(directory, dest_path, keep_names) + count


def read_and_store_directory(directory: str, dest_path: str, keep_names: bool) -> int:
    folder.read(directory)
    folder.drop_duplicates()
    folder.save_paths()
    folder.update_filmchen_and_locations()
    folder.update_names(destination_folder=dest_path,
                        catalog_entry=True,
                        name_from_captured_date=True,
                        name_from_modified_date=False,
                        keep_manual_names=True)

    stored_files = store.list(folder.files)
    copy_to_nas_catalog(stored_files)
    copy_to_dropbox_catalog(stored_files)
    print(f"Added from {directory} : {len(stored_files)}")
    return len(stored_files)


def copy_to_nas_catalog(stored_items):
    for item in stored_items:
        source = item.original_path
        dest_path = os.path.join(dest_root, item.path)
        dest = os.path.join(dest_path, item.name)
        if not os.path.exists(dest_path):
            pathlib.Path(dest_path).mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, dest)


def copy_to_dropbox_catalog(stored_items):
    for item in stored_items:
        source = item.original_path
        dest_path = os.path.join(dbox_root, item.path)
        dbox.put_file(source, item.size, dest_path, item.name, item.modified_ts)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="""Import old catalog into new one. 
    The directory structure has meaning here. The data will be taken from the old structure down. 
    Starting from a YEAR we will traverse into the given months and subdirs are kept as such.
    Duplicates in the same dir are not stored, but duplicates in named directories outside of month are.""")
    parser.add_argument('basedir', type=str, help='Base directory of old catalog.')
    parser.add_argument('year', type=str, help='Year to import.')
    parser.add_argument('--nas_root', type=str, help='Use this as catalog root on NAS')
    parser.add_argument('--dropbox_root', type=str, help='Use this as catalog root on Dropbox')
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
    if args.nas_root:
        dest_root = args.nas_root

    dbox_root = config['dropbox_root']
    if args.dropbox_root:
        dest_root = args.dropbox_root

    ignored_dirs = ["_gsdata_"]
    connection = elastic.Connection(args.host, args.port)
    if args.index:
        connection.index = args.index
    store = elastic.Store(connection)

    folder = data.Folder()
    dbox = DBox(True)
    c = walk_year(import_path, args.year)

    print(f"Added {c} entries to catalog.")
