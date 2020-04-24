import os
import sys
import re
import argparse
import default_args
import constants
from catalog_files import CatalogFiles


def walk_year(directory_name: str, dest_path: str) -> int:
    months = constants.get_months()
    count = 0
    with os.scandir(directory_name) as iterator:
        for item in iterator:
            if item.is_dir():
                if args.month and item.name != args.month:
                    continue
                if item.name in months:
                    count += cat_folder.import_old_dir(item.path, os.path.join(dest_path, item.name), is_month=True)
                else:
                    count += cat_folder.import_old_dir(item.path, os.path.join(dest_path, item.name))

    return count


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="""Import old catalog into new one. 
    The directory structure has meaning here. The data will be taken from the old structure down. 
    Starting from a YEAR we will traverse into the given months and subdirs are kept as such.
    Duplicates in the same dir are not stored, but duplicates in named directories outside of month are.""")
    parser.add_argument('basedir', type=str, help='Base directory of old catalog.')
    parser.add_argument('year', type=str, help='Year to import.')
    parser.add_argument('--dropbox', action='store_true', help='Also create the dropbox copy. Defaults to FALSE')
    parser.add_argument('--nas_root', type=str, help='Use this as catalog root on NAS')
    parser.add_argument('--dropbox_root', type=str, help='Use this as catalog root on Dropbox')
    parser.add_argument('--month', type=str, help='Only catalog the given month.')
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

    index = ""
    if args.index:
        index = args.index

    cat_folder = CatalogFiles(args.host, args.port, index=index, dropbox=args.dropbox)
    if args.nas_root:
        cat_folder.nas_root = args.nas_root
    if args.dropbox_root:
        cat_folder.dropbox_root = args.dropbox_root

    c = walk_year(import_path, args.year)

    print(f"Added {c} entries to catalog.")
