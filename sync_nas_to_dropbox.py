import argparse
import default_args
from catalog import CatalogFiles
from elastic import Retrieve
from data import DBoxError

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="""Scan the catalog for entries where the NAS copy is there
    but the dropbox copy is not yet available.""")
    parser.add_argument('--limit', '-l', type=int, help='Just do it for so many files', default=0)
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output, print each file name copied')
    parser.add_argument('--nas_root', type=str, help='Use this as catalog root on NAS')
    parser.add_argument('--dropbox_root', type=str, help='Use this as catalog root on Dropbox')
    default_args.default_arguments(parser)
    args = parser.parse_args()

    index = ""
    if args.index:
        index = args.index

    cat_folder = CatalogFiles(args.host, args.port, index=index, dropbox=True)
    retrieve = Retrieve(cat_folder.connection)

    if args.nas_root:
        cat_folder.nas_root = args.nas_root
    if args.dropbox_root:
        cat_folder.dropbox_root = args.dropbox_root

    n = 0
    for entry in retrieve.on_nas_but_not_on_dropbox(args.limit):
        entry.set_original_path_on_nas(cat_folder.nas_root)
        try:
            cat_folder.copy_item_to_dropbox(entry)
        except DBoxError as e:
            print("Ignoring : ", str(e))
        else:
            cat_folder.update({"dropbox": True}, entry.id)
            n += 1
            if args.verbose:
                print(f"Copied {entry.full_path}")

    print(f"Copied {n} entries from NAS to dropbox.")
