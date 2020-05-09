from catalog.catalog import Catalog
import os


class CatalogDropbox(Catalog):

    def __init__(self, host: str, port: int, index: str = "", nas: bool = False, verbose: bool = True,
                 dryrun: bool = False, move_files: bool = False):
        super().__init__(host, port, index, True, verbose, dryrun)
        self._nas = nas
        self._move = move_files

    def is_valid(self, directory):
        return self._dbox.is_dir(directory)

    def catalog_dir(self, directory: str, recurse: bool = False, limit: int = None) -> int:
        self._folder.dbox_stream(self._dbox.entries_in_dir(directory, recurse, limit))
        self._folder.drop_duplicates()
        self._folder.save_paths(True)   # always check the checksum when storing into the catalog
        self._folder.update_names(nas=self._nas,
                                  dropbox=True,
                                  name_from_modified_date=True,
                                  keep_manual_names=False)
        self._folder.update_video_path()
        self._folder.update_name_from_location()
        if self._verbose and not self._dryrun:
            self._folder.print_folders()

        return self.do_copy()

    def do_copy(self):
        stored_files = self._store.list(self._folder.files, dryrun=self._dryrun)
        if self._verbose and not self._dryrun:
            self.print_target_dirs(stored_files)
        self.copy_to_dropbox_catalog(stored_files)
        if self._nas and not self._dryrun:
            self.download_to_nas(stored_files)
        return len(stored_files)

    def copy_to_dropbox_catalog(self, stored_files):
        self._dbox.copy_batch_init(self._move)
        for item in stored_files:
            dest_path = os.path.join(self._dropbox_root, item.full_path)
            if self._dryrun:
                print(f"{item.original_path} -> {dest_path}")
            else:
                self._dbox.add_copy_batch(item.original_path, dest_path)
        if not self._dryrun:
            failures = self._dbox.do_copy_batch()
            if len(failures) > 0:
                for item in stored_files:
                    if item.original_path in failures:
                        stored_files.remove(item)          # failures will not be copied down from NAS
                        self._delete.checksum(item.checksum)    # remove failed uploads from catalog again

    def download_to_nas(self, stored_files):
        for item in stored_files:
            self.download_item(item)

    def download_item(self, item):
        dest_path = os.path.join(self.nas_root, item.full_path)
        self._dbox.download_file(os.path.join(self._dropbox_root, item.full_path), dest_path)
