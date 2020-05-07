import os
import sys
import argparse
from tools import default_args
from catalog import CatalogFiles


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="""Upload the given directory into the catalog.
    Files will be copied or moved, default is just to copy.""")
    parser.add_argument('directory', type=str, help='Full path of directory to upload.')
    parser.add_argument('--recursive', '-r', action='store_true', help='Recurse into subdirectories. Defaults to FALSE')
    parser.add_argument('--quiet', '-q', action='store_true', help='Recurse into subdirectories. Defaults to FALSE')
    parser.add_argument('--dryrun', '-d', action='store_true', help='Recurse into subdirectories. Defaults to FALSE')
    parser.add_argument('--dropbox', action='store_true', help='Also create the dropbox copy. Defaults to FALSE')
    parser.add_argument('--nas_root', type=str, help='Use this as catalog root on NAS')
    parser.add_argument('--dropbox_root', type=str, help='Use this as catalog root on Dropbox')
    default_args.default_arguments(parser)
    args = parser.parse_args()

    if not os.path.isdir(args.directory):
        print(f"Invalid directory {args.directory}")
        sys.exit(-1)

    index = ""
    if args.index:
        index = args.index

    cat_folder = CatalogFiles(args.host, args.port, index=index, dropbox=args.dropbox, verbose=not args.quiet,
                              dryrun=args.dryrun)
    if args.nas_root:
        cat_folder.nas_root = args.nas_root
    if args.dropbox_root:
        cat_folder.dropbox_root = args.dropbox_root

    c = cat_folder.catalog_dir(args.directory, recurse=args.recursive)

    if not args.quiet:
        if args.dryrun:
            print(f"Would have added {c} files to catalog")
        else:
            print(f"Added {c} entries to catalog.")
