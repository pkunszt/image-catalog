import os
import argparse


def walktree(directory_name: str):
    # scan the directory: fetch all data for files
    with os.scandir(directory_name) as iterator:
        for item in iterator:
            if item.is_dir() and args.recursive:
                walktree(item.path)
            if not item.name.startswith('.') and item.is_file():
                types.add(os.path.splitext(item.name)[1].lower())


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='List all file types found in the given directory')
    parser.add_argument('dirname', type=str, help='name of directory to catalog')
    parser.add_argument('--recursive', '-r', action='store_true', help='recurse into subdirectories. Default: false')
    args = parser.parse_args()

    types = set()
    walktree(args.dirname)
    print(types)
