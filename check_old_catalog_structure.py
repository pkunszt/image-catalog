import os
import argparse
import re
from constants import get_months


def checkmonths(directory_name: str):
    months = {
        v: k
        for k, v in enumerate(get_months(), 1)
    }
    extra_found = []
    with os.scandir(directory_name) as iterat:
        for it in iterat:
            if it.name.startswith('.'):
                continue
            if it.is_dir() and it.name in months.keys():
                months.pop(it.name)
            else:
                extra_found.append(it.name)
    return extra_found, months.keys()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Check old catalog structure: Names of months in years')
    parser.add_argument('basedir', type=str, help='name of directory of old catalog')
    args = parser.parse_args()

    types = set()
    year = re.compile("\d\d\d\d")
    with os.scandir(args.basedir) as iterator:
        for item in iterator:
            if item.is_dir() and year.match(item.name):
                print(f"{item.name}    ---------------------------------------- ")
                extra, missing = checkmonths(item.path)
                if extra:
                    print(f"Extra found: {extra}")
                if missing:
                    print(f"Not there: {list(missing)}")
