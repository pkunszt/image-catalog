import os

import dropbox
import dropbox.files
import dropbox.exceptions
import json


class DBoxError(dropbox.exceptions.DropboxException):
    def __init__(self, message: str):
        super().__init__(message)


class DBox:
    _config: dict = None
    _full_dbox: dropbox.Dropbox = None
    _catalog_dbox: dropbox.Dropbox = None
    UPLOAD_SIZE: int = 50 * 1024 * 1024
    MAX_SIZE: int = 100 * 1024 * 1024

    def __init__(self, full: bool = False):
        self._dbox = DBox._full_dropbox() if full else DBox._catalog_dropbox()

    @staticmethod
    def _get_config():
        if not DBox._config:
            with open("./config.json", 'r') as fp:
                DBox._config = json.load(fp)
        return DBox._config

    @staticmethod
    def _full_dropbox():
        if not DBox._full_dbox:
            DBox._full_dbox = dropbox.Dropbox(DBox._get_config()['dbox_full_token'])
        return DBox._full_dbox

    @staticmethod
    def _catalog_dropbox():
        if not DBox._catalog_dbox:
            DBox._catalog_dbox = dropbox.Dropbox(DBox._get_config()['dbox_catalog_token'])
        return DBox._catalog_dbox

    def list_dir(self, path: str, recurse: bool = False) -> str:
        result_list = self._dbox.files_list_folder(path, recursive=recurse)
        for item in result_list.entries:
            if type(item) is dropbox.files.FileMetadata:
                yield item.path_display
        while result_list.has_more:
            result_list = self._dbox.files_list_folder_continue(result_list.cursor)
            for item in result_list.entries:
                if type(item) is dropbox.files.FileMetadata:
                    yield item.path_display

    def get_metadata(self, path: str) -> dict:
        file_metadata = self._dbox.files_get_metadata(path, include_media_info=True)
        result = dict(
            size=file_metadata.size,
            checksum=file_metadata.content_hash,
            modified=int(file_metadata.client_modified.timestamp()*1000),
            dropbox_path=True,
            path=file_metadata.path_display
        )
        if hasattr(file_metadata, "media_info") and file_metadata.media_info is not None:
            media_metadata = file_metadata.media_info.get_metadata()
            if hasattr(media_metadata, "time_taken") and media_metadata.time_taken is not None \
                    and media_metadata.time_taken.timestamp() > 0:
                result.update(captured=int(media_metadata.time_taken.timestamp()*1000))
            if hasattr(media_metadata, "dimensions") and media_metadata.dimensions is not None:
                result.update(dimensions=f"{media_metadata.dimensions.width}x{media_metadata.dimensions.height}")
            if hasattr(media_metadata, "location") and media_metadata.location is not None:
                loc = media_metadata.location
                result.update(location=f"{round(loc.latitude, 5)},{round(loc.longitude, 5)}")
            if hasattr(media_metadata, "duration") and media_metadata.duration is not None \
                    and media_metadata.duration > 0:
                result.update(duration=int(media_metadata.duration)/1000)  # dropbox extracts duration in millisec

        return result

    def entries_in_dir(self, path: str, recurse: bool = False) -> dict:
        for file in self.list_dir(path, recurse):
            yield self.get_metadata(file)

    def exists(self, path) -> bool:
        """Check if a path (directory or file) exists."""
        try:
            self._dbox.files_get_metadata(path)
        except dropbox.exceptions.ApiError as apie:
            err = apie.error
            if err.get_path().is_not_found():
                return False
            else:
                raise DBoxError(repr(err))
        else:
            return True

    def is_dir(self, path) -> bool:
        """Check if a path is a directory. If the path does not exist, it just returns false"""
        try:
            self._dbox.files_list_folder(path, recursive=False, include_deleted=False)
        except dropbox.exceptions.ApiError as apie:
            err = apie.error
            if err.get_path().is_not_folder() or err.get_path().is_not_found():
                return False
            else:
                raise DBoxError(repr(err))
        else:
            return True

    def put_file(self, source: str, size: int, dest_dir: str, dest_name: str, modified):
        if not self.exists(dest_dir):
            self._dbox.files_create_folder_v2(dest_dir)

        try:
            if size > DBox.MAX_SIZE:
                self.put_large_file(source, size, dest_dir, dest_name, modified)
            else:
                with open(source, "rb") as file:
                    contents = file.read()
                    self._dbox.files_upload(contents, os.path.join(dest_dir, dest_name), client_modified=modified)
        except dropbox.exceptions.DropboxException as e:
            print("Dropbox Exception: ", e.request_id, e)
            raise DBoxError(repr(e))

    def put_large_file(self, source: str, size: int, dest_dir: str, dest_name: str, modified):
        with open(source, "rb") as file:
            contents = file.read(DBox.UPLOAD_SIZE)
            start = self._dbox.files_upload_session_start(contents)
            offset = len(contents)

            while len(contents) == DBox.UPLOAD_SIZE:
                cursor = dropbox.files.UploadSessionCursor(start.session_id, offset)
                contents = file.read(DBox.UPLOAD_SIZE)
                if len(contents) == DBox.UPLOAD_SIZE:
                    self._dbox.files_upload_session_append_v2(contents, cursor)
                    offset += len(contents)

            commit = dropbox.files.CommitInfo(os.path.join(dest_dir, dest_name), client_modified=modified)
            if offset+len(contents) != size:
                print(f"""Problem writing to Dropbox {dest_dir}/{dest_name}: 
                Size assertion is wrong {size} != {offset+len(contents)}""")
                raise ValueError("Problem")
            self._dbox.files_upload_session_finish(contents, cursor, commit)

    def copy_file(self, from_path, to_path, create_folders: bool = False):
        try:
            self._dbox.files_copy_v2(from_path, to_path)
        except dropbox.exceptions.ApiError as apie:
            if create_folders:
                err = apie.error
                if err.get_path().is_not_found():
                    self.create_folder(os.path.basename(to_path))
                    self.copy_file(from_path, to_path)
            else:
                raise DBoxError(repr(apie))

    def create_folder(self, path):
        self._dbox.files_create_folder_v2(path)

    def download_file(self, path, destination):
        self._dbox.files_download_to_file(destination, path)
