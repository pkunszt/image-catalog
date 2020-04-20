import os
import sys
import re
import argparse
import elastic
import data
import default_args
import constants


def walk_year(directory_name: str):
    months = constants.get_months()
    count = 0
    with os.scandir(directory_name) as iterator:
        for item in iterator:
            if item.is_dir():
                if item.name in months:
                    count += catalog_month(item.path)
                else:
                    count += catalog_as_is(item.path)

    return count


def catalog_month(month_directory: str):
    count = 0
    with os.scandir(month_directory) as iterator:
        for item in iterator:
            if item.is_dir():
                count += catalog_as_is(item.path)

    folder.read(month_directory)
    folder.drop_duplicates()
    count += store.list(folder.files, name_from_captured_date=True)
    return count


def catalog_as_is(directory: str):
    count = 0
    if directory in ignored_dirs:
        return 0
    with os.scandir(directory) as iterator:
        for item in iterator:
            if item.is_dir():
                count += catalog_as_is(item.path)

    folder.read(directory)
    folder.drop_duplicates()
    count += store.list(folder.files, name_from_captured_date=True)
    return count


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="""Import old catalog into new one. 
    The directory structure has meaning here. The data will be taken from the old structure down. 
    Starting from a YEAR we will traverse into the given months and subdirs are kept as such.
    Duplicates in the same dir are not stored, but duplicates in named directories outside of month are.""")
    parser.add_argument('basedir', type=str, help='Base directory of old catalog.')
    parser.add_argument('year', type=str, help='Year to import.')
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

    ignored_dirs = ["_gsdata_"]
    connection = elastic.Connection(args.host, args.port)
    if args.index is not None:
        connection.index = args.index
    store = elastic.Store(connection)

    folder = data.Folder()
    c = walk_year(import_path)

    print(f"Added {c} entries to catalog.")
