import argparse
import json
from data import Folder

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='List all image and video files in the given directory')
    parser.add_argument('dirname', type=str, help='name of directory to catalog')
    args = parser.parse_args()

    folder = Folder()
    folder.read(args.dirname)
    print(json.dumps(folder.file_list_as_dict(), indent=4))
    if len(folder.invalid_types) > 0:
        print("Invalid file types found:")
        print(folder.invalid_types)
