import sys
import json
from directory import Reader

if __name__ == '__main__':
    image_dir = Reader(sys.argv[1])
    image_list = image_dir.file_list_as_dict()
    print(json.dumps(image_list, indent=4))
    if len(image_dir.invalid_types) > 0:
        print("Invalid file types found:")
        print(image_dir.invalid_types)
