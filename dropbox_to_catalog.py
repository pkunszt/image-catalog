import os
import sys
import argparse
from tools import elastic_arguments, upload_arguments, root_arguments
from catalog import CatalogDropbox


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="""Load the given dropbox path into the catalog.
    The dropbox catalog will be used, meaning that all files in the dropbox directory will be copied to 
    the catalog location on dropbox. It is a dropbox-to-dropbox copy operation. 
    Files are downloaded to the NAS copy of the catalog only if explicitly requested using the --nas flag.
    The nas catalog can be syncronized also later using the sync_dropbox_to_nas tool.""")
    parser.add_argument('directory', type=str, help='Full path of dropbox directory to load.')
    upload_arguments(parser)
    parser.add_argument('--nas', action='store_true', help='Also create the NAS copy. Defaults to FALSE')
    root_arguments(parser)
    elastic_arguments(parser)
    args = parser.parse_args()

    index = ""
    if args.index:
        index = args.index

    cat_folder = CatalogDropbox(args.host, args.port, index=index, nas=args.nas, verbose=not args.quiet,
                                dryrun=args.dryrun)
    if args.nas_root:
        cat_folder.nas_root = args.nas_root
    if args.dropbox_root:
        cat_folder.dropbox_root = args.dropbox_root

    if not cat_folder.is_valid(args.directory):
        print(f"Invalid directory {args.directory}")
        sys.exit(-1)

    c = cat_folder.catalog_dir(args.directory, recurse=args.recursive)

    if not args.quiet:
        if args.dryrun:
            print(f"Would have added {c} files to catalog")
        else:
            print(f"Added {c} entries to catalog.")
