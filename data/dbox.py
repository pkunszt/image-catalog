import dropbox
import json


class DBox:
    _config: dict = None
    _full_dbox: dropbox.Dropbox = None
    _catalog_dbox: dropbox.Dropbox = None

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
            yield item.path_display
        while result_list.has_more:
            result_list = self._dbox.files_list_folder_continue(result_list.cursor)
            for item in result_list.entries:
                yield item.path_display

    def get_metadata(self, path: str) -> dict:
        file_metadata = self._dbox.files_get_metadata(path, include_media_info=True)
        result = dict(
            size=file_metadata.size,
            checksum=file_metadata.content_hash,
            modified=int(file_metadata.client_modified.timestamp()*1000),
            dropbox_path=True
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
                result.update(duration=int(media_metadata.duration/1000))  # dropbox extracts duration in millisec

        return result

    def entries_in_dir(self, path:str, recurse: bool = False) -> dict:
        for file in self.list_dir(path, recurse):
            yield self.get_metadata(file)
