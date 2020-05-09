import os
import argparse
import sys

from data import Factory, Entry, FactoryError, DBox
from tools import elastic_arguments, root_arguments, read_config
import elastic


global local_limit


def process_item(item):
    cat_item: Entry = next(reader.get_by_checksum(item.checksum), None)
    if cat_item:
        if os.path.exists(os.path.join(config['nas_root'], cat_item.full_path)):
            if not args.dryrun:
                os.remove(item.full_path)
            print(f"Delete: {item.full_path}")
        else:
            print(f"****** NoFile!: {cat_item.full_path} although in catalog")
    else:
        print(f"NotCat: {item.full_path}")


def check_dir(directory: str, limit: int):
    global local_limit
    with os.scandir(directory) as iterator:
        for item in iterator:
            if 0 < limit < local_limit:
                break
            if item.is_dir():
                if args.recursive:
                    check_dir(item.path, limit)
            else:
                try:
                    process_item(Factory.from_path(item.path))
                except FactoryError:
                    print(f"NotImg: {item.path}")
                    continue     # ignore nonvideo / nonimage files.
                finally:
                    local_limit += 1

    if not os.listdir(directory):  # remove empty directories as well
        if not args.dryrun:
            os.rmdir(directory)
        print(f"RMDIR : {directory}")


def check_dropbox_dir(directory: str, limit):
    dbox = DBox(True)
    for item in dbox.list_dir(directory, recurse=args.recursive, limit=None if limit < 0 else limit,
                              path_only=False):
        cat_item: Entry = next(reader.get_by_checksum(item.content_hash), None)
        if cat_item:
            dbox_path = os.path.join(config['dropbox_root'], cat_item.full_path)
            if dbox.exists(dbox_path):
                if not args.dryrun:
                    dbox.remove(item.path_display)
                print(f"Delete: {item.path_display} - is in catalog as {dbox_path}")
            else:
                print(f"****** NoFile!: {dbox_path} is not there although it is in catalog. Source: {item.path_display}")
                if not args.dryrun:
                    dbox.move_file(item.path_display, dbox_path)
        else:
            print(f"NotCat: {item.path_display}")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="""Takes a directory argument. Removes images and videos from the
    given directory if they are already in the catalog. This validates also whether the file actually exists.
    Default is to search for the file locally on the NAS but if the --dropbox argument is given then the dropbox
    will be searched and the directory path is expected to be on dropbox.""")
    parser.add_argument('directory', type=str, help='Full path of local or dropbox directory to check.')
    parser.add_argument('--recursive', '-r', action='store_true', help='Recurse into subdirectories. Defaults to FALSE')
    parser.add_argument('--dryrun', '-d', action='store_true', help="""Do a dry run only, print what would be done. """)
    parser.add_argument('--limit', '-l', type=int, help='Limit the number of files processed', default=-1)
    parser.add_argument('--dropbox', action='store_true', help='Do this on a dropbox folder. Check against dropbox.')
    root_arguments(parser)
    elastic_arguments(parser)
    args = parser.parse_args()

    connection = elastic.Connection(args.host, args.port)
    if args.index is not None:
        connection.index = args.index

    reader = elastic.Retrieve(connection)

    config = read_config()
    if args.nas_root:
        config['nas_root'] = args.nas_root
    if args.dropbox_root:
        config['dropbox_root'] = args.dropbox_root

    if not args.dropbox and args.directory.startswith(config['nas_root']):
        print("Invalid directory: Cannot run with a directory from inside NAS_ROOT")
        sys.exit(-1)
    elif args.dropbox and args.directory.startswith(config['dropbox_root']):
        print("Invalid directory: Cannot run with a directory from inside NAS_ROOT")
        sys.exit(-1)

    local_limit = 0
    if args.dropbox:
        check_dropbox_dir(args.directory, args.limit)
    else:
        check_dir(args.directory, args.limit)
