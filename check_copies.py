import argparse
import os

from tools import root_arguments, read_config, Constants

nas_list = []
dropbox_list = []
loading_bar = 0
loading_increase = 10000


def get_files(path, start):
    for item in os.listdir(path):
        if item not in Constants.ignored_paths:
            yield os.path.join(path, item)[start:]


def walktree(directory_name: str, use_list: list, start: int, counter: int = 0):
    global loading_bar
    with os.scandir(directory_name) as dir_iterator:
        for it in dir_iterator:
            if it.name.startswith('.'):
                continue
            if it.is_dir():
                walktree(it.path, use_list, start, counter)
                use_list.extend(get_files(it.path, start))  # strip the root name

    counter += len(use_list)
    if counter > loading_bar:
        print(loading_bar, end='..', flush=True)
        loading_bar += loading_increase


def to_file(name, my_list):
    with open(name, 'w', encoding='utf-8') as file:
        file.writelines(line + '\n' for line in my_list)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="""Scan both locations using os.listdir, which is fast.
    Make use of the fact that Dropbox creates the dir entries locally. Check if both copies exist,
    create output files with one line each for items that are on only nas, or only dropbox.
    Running this only makes sense if the sync between the two does not return anything to sync.""")
    parser.add_argument('year', nargs='?', type=str, help='Which year dir to check.')
    root_arguments(parser)
    args = parser.parse_args()

    config = read_config()
    nas_root = config['nas_root']
    dropbox_root = config['dropbox_local']
    if args.year:
        nas_root = os.path.join(nas_root, args.year)
        dropbox_root = os.path.join(dropbox_root, args.year)

    walktree(nas_root, nas_list, len(nas_root))
    loading_bar = 0
    print(' ')
    walktree(dropbox_root, dropbox_list, len(dropbox_root))
    print(' ')

    nas_list = sorted(nas_list)
    dropbox_list = sorted(dropbox_list)
    nas_only = []
    dropbox_only = []

    iterate_over = nas_list
    min_len = len(nas_list)
    if len(nas_list) > len(dropbox_list):
        min_len = len(dropbox_list)
    diff_len = False
    if len(nas_list) != len(dropbox_list):
        diff_len = True

    print(len(nas_list), len(dropbox_list), len(iterate_over))

    nas_index = 0
    dropbox_index = 0
    change_detected = 0
    for i in range(0, min_len):
        if nas_list[nas_index] != dropbox_list[dropbox_index]:
            change: bool = True
            change_detected += 1
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

        nas_index += 1
        dropbox_index += 1
        if nas_index >= len(nas_list) or dropbox_index >= len(dropbox_list):
            break

    print(nas_index, dropbox_index, change_detected)
    if diff_len:
        for i in range(nas_index, len(nas_list)):
            nas_only.append(nas_list[i])
        for i in range(dropbox_index, len(dropbox_list)):
            dropbox_only.append(dropbox_list[i])

    if len(nas_only) > 0:
        print(f"There are {len(nas_only)} files only on NAS. See nas_only.txt.")
        to_file('nas_only.txt', nas_only)
    if len(dropbox_only) > 0:
        print(f"There are {len(dropbox_only)} files only on Dropbox. See dropbox_only.txt.")
        to_file('dropbox_only.txt', dropbox_only)
