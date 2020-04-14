import os
import argparse
import elastic
import directory
import default_args


def walktree(directory_name: str):
    with os.scandir(directory_name) as iterator:
        for item in iterator:
            if item.is_dir() and args.recursive:
                walktree(item.path)
    folder.read(directory_name)
    global c
    c = c + store.list(folder.files)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Catalog all image and video files in the given directory')
    parser.add_argument('dirname', type=str, help='name of directory to catalog')
    parser.add_argument('--recursive', '-r', action='store_true', help='recurse into subdirectories. Default: false')
    parser.add_argument('--allow_duplicates', '-d', action='store_true', help='Duplicates are not ok by default.')
    default_args.default_arguments(parser)
    args = parser.parse_args()

    connection = elastic.Connection(args.host, args.port)
    if args.index is not None:
        connection.index = args.index
    store = elastic.Store(connection, allow_duplicates=args.allow_duplicates)

    folder = directory.Reader()
    c = 0
    walktree(args.dirname)
    print(f"Added {c} entries to catalog.")
    print(f"Invalid types found: {folder.invalid_types}")
