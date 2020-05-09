import argparse
from tools import elastic_arguments, root_arguments
from catalog import CatalogDropbox
from elastic import Retrieve, Delete
from data import DBoxError, DBoxNoFileError

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="""Scan the catalog for entries where the dropbox copy is there
    but the NAS copy is not yet available.""")
    parser.add_argument('--limit', '-l', type=int, help='Just do it for so many files', default=0)
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output, print each file name copied')
    root_arguments(parser)
    elastic_arguments(parser)
    args = parser.parse_args()

    index = ""
    if args.index:
        index = args.index

    cat_folder = CatalogDropbox(args.host, args.port, index=index, nas=True)
    retrieve = Retrieve(cat_folder.connection)
    delete = Delete(cat_folder.connection)

    if args.nas_root:
        cat_folder.nas_root = args.nas_root
    if args.dropbox_root:
        cat_folder.dropbox_root = args.dropbox_root

    n = 0
    for entry in retrieve.on_dropbox_but_not_on_nas(args.limit):
        entry.prepend_original_path(cat_folder.dropbox_root)
        try:
            cat_folder.download_item(entry)
        except DBoxNoFileError as e:
            print(e)
            print("file is in the catalog but not on dropbox. removing from catalog")
            delete.id(entry.id)
        except DBoxError as e:
            print("Ignoring : ", str(e))
        else:
            cat_folder.update({"nas": True}, entry.id)
            n += 1
            if args.verbose:
                print(f"Copied {entry.full_path}")

    print(f"Copied {n} entries from dropbox to NAS.")
