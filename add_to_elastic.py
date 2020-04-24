import os
import argparse
import elastic
import data
import default_args


def walktree(directory_name: str):
    with os.scandir(directory_name) as iterator:
        for item in iterator:
            if item.is_dir() and args.recursive:
                walktree(item.path)
    folder.read(directory_name)
    global c
    c = c + store.list(folder.files)


def walkdbox(dirname: str):
    dbox = data.DBox(True)

    for item in dbox.list_dir(dirname, args.recursive):
        try:
            entry = data.Factory.from_dropbox(item)
        except data.FactoryError:
            invalid_types.add(os.path.splitext(item)[1])
        else:
            yield entry


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="""Add all image and video files in the given directory to 
    the elastic catalog. The files are not catalogued, ie moved to the NAS and Dropbox, but are now in elastic,
    ready for further processing.""")
    parser.add_argument('dirname', type=str, help='name of directory to catalog')
    parser.add_argument('--recursive', '-r', action='store_true', help='recurse into subdirectories. Default: false')
    parser.add_argument('--dropbox', action='store_true', help="""add files from dropbox. The given directory 
    needs to be relative to the dropbox root and start with '/'. Default: false""")
    default_args.default_arguments(parser)
    args = parser.parse_args()

    connection = elastic.Connection(args.host, args.port)
    if args.index is not None:
        connection.index = args.index
    store = elastic.Store(connection)

    if args.dropbox:
        invalid_types = set()
        c = store.list(walkdbox(args.dirname))

    else:
        folder = data.Folder()
        c = 0
        walktree(args.dirname)
        invalid_types = folder.invalid_types

    print(f"Added {c} entries to catalog.")
    print(f"Not added because of duplicates: {store.not_stored}")
    print(f"Data Types not added: {invalid_types}")
