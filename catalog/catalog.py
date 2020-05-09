import data
import elastic
from tools import read_config


class Catalog:
    _ignored_dirs = ["_gsdata_"]

    def __init__(self, host: str, port: int, index: str = "", dropbox: bool = False,
                 verbose: bool = True, dryrun: bool = False):
        self._folder = data.Folder()
        self._dropbox = dropbox
        self._verbose = verbose
        self._dryrun = dryrun
        self._connection = elastic.Connection(host, port)
        if index:
            self._connection.index = index
        self._store = elastic.Store(self._connection)
        self._delete = elastic.Delete(self._connection)
        self._dbox = data.DBox(True)

        config = read_config()
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

    @staticmethod
    def print_target_dirs(file_list):
        dirs = dict()
        print(f"Storing {len(file_list)} files")
        for entry in file_list:
            dirs.setdefault(entry.path, []) \
                .append(0)
        for item in sorted(list(dirs.keys())):
            print(f"{item} : {len(dirs[item])}")

    def update(self, change, _id):
        self._store.update(change, _id)
