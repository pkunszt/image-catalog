import os
import sys
import argparse
import re
import default_args
import elastic

retrieve: elastic.Retrieve
date_pattern = re.compile(r'\d{4}-\d\d-\d\d \d\d-\d\d-\d\d\.\w+')  # regex for date format


def get_duplicates_in_dir(dirname: str = None):
    global retrieve
    entry_list = dict()
    for entry in retrieve.all_entries(dirname):
        entry_list.setdefault(entry.checksum+entry.path, [])\
            .append({'id': entry.meta.id, 'path': entry.path, 'name': entry.name})

    for h, item in entry_list.items():
        if len(item) > 1:
            yield item


def select_name_to_keep(image_list) -> dict:
    for im in image_list:
        if date_pattern.match(im['name']):
            return im
    return sorted(image_list, key=lambda entry: entry['name'])[0]


def main(arg):
    global retrieve

    parser = argparse.ArgumentParser(description="""Delete duplicates in the same directory. 
    You need to provide the directory to find duplicates in. This will be based on the catalog entries
    and not on what is actually on disk, make sure you add everything to the catalog and sync with it
    before running this so that it will execute correctly. It is assumed that 
    The file name with the name that makes most sense is kept. If one of the names""")
    parser.add_argument('dirname', nargs='?', type=str, help='name of directory to do deduplication in')
    parser.add_argument('--dryrun', action='store_true', help="don't delete, just print. Default: false")
    default_args.default_arguments(parser)
    args = parser.parse_args(arg)

    connection = elastic.Connection(args.host, args.port)
    if args.index is not None:
        connection.index = args.index

    retrieve = elastic.Retrieve(connection)
    delete = elastic.Delete(connection)

    if args.dirname:
        dir_list = (args.dirname, )
    else:
        dir_list = retrieve.all_paths()

    for d in dir_list:
        print(f"Scanning {d}")
        for duplicate_list in get_duplicates_in_dir(d):
            keep = select_name_to_keep(duplicate_list)
            print(f"Keeping {keep['name']}")
            for to_delete in duplicate_list:
                if to_delete['id'] != keep['id']:
                    print(f" .... Deleting {to_delete['name']}")
                    if not args.dryrun:
                        os.remove(os.path.join(to_delete['path'], to_delete['name']))
                        delete.id(to_delete['id'])


if __name__ == '__main__':
    main(sys.argv[1:])