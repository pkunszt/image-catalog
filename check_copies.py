import argparse
import os

from tools import root_arguments, read_config

nas_list = []
dropbox_list = []


def walktree(directory_name: str, use_list: list, start: int):
    with os.scandir(directory_name) as dir_iterator:
        for it in dir_iterator:
            if it.name.startswith('.'):
                continue
            if it.is_dir():
                walktree(it.path, use_list, start)
                use_list.extend(item[start:] for item in os.listdir(it.path))  # strip the root name


def to_file(name, my_list):
    with open(name, 'w', encoding='utf-8') as file:
        file.writelines(line + '\n' for line in my_list)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="""Scan both locations using os.listdir, which is fast.
    Make use of the fact that Dropbox creates the dir entries locally. Check if both copies exist,
    create output files with one line each for items that are on only nas, or only dropbox.
    Running this only makes sense if the sync between the two does not return anything to sync.""")
    parser.add_argument('year', type=str, help='Which year dir to check.')
    root_arguments(parser)
    args = parser.parse_args()

    config = read_config()
    walktree(os.path.join(config['nas_root'], args.year), nas_list, len(config['nas_root']))
    walktree(os.path.join(config['dropbox_local'], args.year), dropbox_list, len(config['dropbox_local']))

    nas_list = sorted(nas_list)
    dropbox_list = sorted(dropbox_list)
    nas_only = []
    dropbox_only = []

    iterate_over = nas_list
    if len(nas_list) > len(dropbox_list):
        iterate_over = dropbox_list

    print(len(nas_list), len(dropbox_list), len(iterate_over))

    nas_index = 0
    dropbox_index = 0
    for i in range(0, len(iterate_over)):
        if nas_list[nas_index] == dropbox_list[dropbox_index]:
            continue
        change: bool = True
        while change:
            change = False
            while nas_list[nas_index] > dropbox_list[dropbox_index]:
                dropbox_only.append(dropbox_list[dropbox_index])
                dropbox_index += 1
                change = True
            while nas_list[nas_index] < dropbox_list[dropbox_index]:
                nas_only.append(nas_list[nas_index])
                nas_index += 1
                change = True

    if len(nas_only) > 0:
        print(f"There are {len(nas_only)} files only on NAS. See nas_only.txt.")
        to_file('nas_only.txt', nas_only)
    if len(dropbox_only) > 0:
        print(f"There are {len(dropbox_only)} files only on Dropbox. See dropbox_only.txt.")
        to_file('dropbox_only.txt', dropbox_only)
