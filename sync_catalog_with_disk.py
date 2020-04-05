import os
import argparse

from directory_util import DirectoryUtil
from elastic_storage import ElasticStorage
from images_in_directory import ImagesInDirectory


class SyncCatalogWithDisk:
    __catalog: ElasticStorage
    __count: int

    def __init__(self, host: str = 'localhost', port: int = 9200):
        if not host:
            host = 'localhost'
        if not port:
            port = 9200
        self.__catalog = ElasticStorage(host, port)
        self.__count = 0

    def sync(self, video: bool = False, directory: str = None, verbose: bool = True):
        self.__count = 0
        for entry in self.__catalog.scan_index(video=video, directory_filter=directory):
            full_path = entry.path+'/'+entry.name
            try:
                st = os.stat(full_path)
            except FileNotFoundError:
                if verbose:
                    print("{0} In catalog but not on disk".format(full_path))
                index = self.__catalog.set_index(video)
                self.__catalog.delete_id(index, entry.meta.id)
                self.__count = self.__count + 1
                continue

            # Now detect if there is a difference
            change = {}
            new_entry = self.entry_to_dict(entry)
            if st.st_size != entry.size:
                if verbose:
                    print("{0} size mismatch: catalog has {1} disk has {2}".format(full_path, entry.size, st.st_size))
                new_entry['size'] = st.st_size
                change['size'] = st.st_size
            if st.st_mtime != entry.created:
                if verbose:
                    print("{0} date mismatch: catalog has {1} disk has {2}".format(full_path, entry.created, 
                                                                                   st.st_mtime))
                new_entry['created'] = st.st_mtime
                change['created'] = st.st_mtime
            new_type: str = DirectoryUtil.get_file_type(full_path)
            if new_type != entry.type:
                if verbose:
                    print("{0} type mismatch: catalog has {1} disk has {2}".format(full_path, entry.type, new_type))
                new_entry['type'] = new_type
                change['type'] = new_type
            new_hash = ImagesInDirectory.get_hash_from_entry(new_entry)
            if new_hash != entry.hash:
                if verbose:
                    print("{0} hash mismatch: catalog has {1} disk has {2}".format(full_path, entry.hash, new_hash))
                change['hash'] = new_hash

            if len(change) > 0:
                self.__catalog.update(change, video=video, _id=entry.meta.id)
                self.__count = self.__count + 1

        return self.__count

    @staticmethod
    def entry_to_dict(entry):
        new_entry = {'name': entry.name,
                     'path': entry.path,
                     'size': entry.size,
                     'created': entry.created,
                     'checksum': entry.checksum,
                     'hash': entry.hash,
                     'type': entry.type,
                     'kind': entry.kind}
        return new_entry


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Sync catalog with the data on disk')
    parser.add_argument('dirname', nargs='?', type=str, help='name of directory to look at')
    parser.add_argument('--video', '-v', action='store_true', help='use the video catalog')
    parser.add_argument('--quiet', '-q', action='store_true', help='no verbose output')
    parser.add_argument('--host', type=str, help='the host where elastic runs. Default: localhost')
    parser.add_argument('--port', type=int, help='the port where elastic runs. Default: 9200')
    args = parser.parse_args()
    sync_catalog = SyncCatalogWithDisk(args.host, args.port)
    print("updated: {0} entries ".format(sync_catalog.sync(video=args.video, directory=args.dirname,
                                                           verbose=not args.quiet)))
