import os
import shutil
import pathlib
import json
import data
import elastic


class CatalogFiles:
    _ignored_dirs = ["_gsdata_"]

    def __init__(self, host: str, port: int, index: str = "", dropbox: bool = False):
        self._folder = data.Folder()
        self._dropbox = dropbox
        self._connection = elastic.Connection(host, port)
        if index:
            self._connection.index = index
        self._store = elastic.Store(self._connection)
        self._dbox = data.DBox(True)

        with open("config.json", 'r') as file:
            config = json.load(file)
        self._nas_root = config['nas_root']
        self._dropbox_root = config['dropbox_root']

    @property
    def nas_root(self):
        return self._nas_root

    @property
    def dropbox_root(self):
        return self._dropbox_root

    @nas_root.setter
    def nas_root(self, name):
        self._nas_root = name

    @dropbox_root.setter
    def dropbox_root(self, name):
        self._dropbox_root = name

    @property
    def connection(self):
        return self._connection

    def catalog_dir(self, directory: str, recurse: bool = False) -> int:
        count = 0
        if directory in self._ignored_dirs:
            return 0
        with os.scandir(directory) as iterator:
            for item in iterator:
                if item.is_dir() and recurse:
                    count += self.catalog_dir(item.path, recurse)

        self.get_files(directory, check=True)
        count += self.read_and_update_directory()
        print(f"Loaded from {directory} : {count}   / Not stored: {self._store.not_stored}")
        return count

    def import_old_dir(self, directory: str, dest_path: str, is_month: bool = False) -> int:
        count = 0
        if directory in self._ignored_dirs:
            return 0
        with os.scandir(directory) as iterator:
            for item in iterator:
                if item.is_dir():
                    count += self.import_old_dir(item.path, os.path.join(dest_path, item.name))

        self.get_files(directory, check=is_month)
        count += self.read_and_import_directory(dest_path, is_month)
        print(f"Imported from {directory} : {count}   / Not stored: {self._store.not_stored}")
        return count

    def get_files(self, directory: str, check: bool = False):
        self._folder.read(directory)
        self._folder.drop_duplicates()
        self._folder.save_paths(check)

    def read_and_update_directory(self):
        self._folder.update_names(nas=True,
                                  dropbox=self._dropbox,
                                  name_from_modified_date=True,
                                  keep_manual_names=False)
        self._folder.update_video_path()
        self._folder.update_name_from_location()

        return self.do_copy()

    def read_and_import_directory(self, dest_path: str, is_month_path: bool) -> int:
        self._folder.update_names(destination_folder=dest_path,
                                  nas=True,
                                  dropbox=self._dropbox,
                                  name_from_modified_date=False,
                                  keep_manual_names=not is_month_path,
                                  is_month=is_month_path)
        if is_month_path:
            self._folder.update_video_path()
        self._folder.update_name_from_location()

        return self.do_copy()

    def do_copy(self):
        stored_files = self._store.list(self._folder.files)
        self.copy_to_nas(stored_files)
        if self._dropbox:
            self.copy_to_dropbox(stored_files)
        return len(stored_files)

    def copy_to_nas(self, stored_items):
        for item in stored_items:
            source = item.original_path
            dest_path = os.path.join(self.nas_root, item.path)
            dest = os.path.join(dest_path, item.name)
            if not os.path.exists(dest_path):
                pathlib.Path(dest_path).mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, dest)

    def copy_to_dropbox(self, stored_items):
        for item in stored_items:
            self.copy_item_to_dropbox(item)

    def copy_item_to_dropbox(self, item):
        source = item.original_path
        dest_path = os.path.join(self.dropbox_root, item.path)
        self._dbox.put_file(source, item.size, dest_path, item.name, item.modified_ts)

    def update(self, change, _id):
        self._store.update(change, _id)