import os
from typing import List, Generator
import reverse_geocoder
import geopy
from constants import Constants
from data.factory import Factory, FactoryError
from data.entry import Entry


class Folder:
    """Class to scan a directory and return a list of entries, either image or video"""
    __file_list: List[Entry]
    __invalid_types_found: set
    __valid_types_found: set
    geo: geopy.geocoders.osm.Nominatim = geopy.geocoders.Nominatim(user_agent="my_catalog")

    def __init__(self):
        self.__file_list = []
        self.__invalid_types_found = set()
        self.__valid_types_found = set()

    def read(self, directory_name: str) -> None:
        """Read from a given directory all image and video files.
        The result can be retrieved as a list of data.entry objects,
        as a list of dictionary objects or as the generator with all entries.
        Entries are images or videos, according to data.image and data.video

        Argument:
        directory_name -- name of the full path of the directory to scan.
        """
        if not os.path.isdir(directory_name):
            raise NotADirectoryError(directory_name + " is not a directory!")
        self.__file_list.clear()

        # scan the directory: fetch all data for files
        with os.scandir(directory_name) as iterator:
            for item in iterator:
                if not item.name.startswith('.') and item.is_file():
                    self.__add_entry(item.path)

    def __add_entry(self, path: str) -> None:
        """Adding an entry, specificity based on whether it is an image or a video. Args stat and path."""
        try:
            item = Factory.from_path(path)
            self.__file_list.append(item)
            self.__valid_types_found.add(item.type)
        except FactoryError:
            self.__invalid_types_found.add(os.path.splitext(path.lower())[1])

    @property
    def invalid_types(self) -> set:
        """Return the set of invalid types found, ie files that have not been processed"""
        return self.__invalid_types_found

    @property
    def valid_types(self) -> set:
        """Return the set of valid types found, ie file types that have been processed"""
        return self.__valid_types_found

    @property
    def file_list(self) -> List[Entry]:
        """Return the list of entries, these will be either Video or Image objects"""
        return self.__file_list

    @property
    def files(self) -> Generator:
        """Return the list as a generator to be iterated through"""
        return (
            entry
            for entry in self.__file_list
        )

    def file_list_as_dict(self) -> List[dict]:
        """Return the list of entries as dictionary objects, to be used in JSON"""
        return [
            entry.to_dict()
            for entry in self.__file_list
        ]

    def drop_duplicates(self):
        """If more than one file in the same directory has the same checksum, just remove duplicates from the list"""
        entry_list = dict()
        for entry in self.file_list:
            entry_list.setdefault(entry.checksum, []).append(entry)

        for h, item in entry_list.items():
            if len(item) > 1:
                for to_delete in item[1:]:
                    self.__file_list.remove(to_delete)

    def save_paths(self):
        for entry in self.file_list:
            entry.save_path()

    def update_filmchen_and_locations(self):
        """In the given list 'move' the movies into 'filmchen' folder and if items have locations
        then resolve the city and 'move' them into a city folder"""
        for entry in self.file_list:
            if entry.kind == Constants.VIDEO_KIND:
                entry.path = os.path.join(entry.path, 'filmchen')
                continue
            if entry.location:
                lat, lon = entry.location.split(',')
                default_name = reverse_geocoder.search([(float(lat), float(lon))])[0]['name']
                alt_names = Folder.geo.reverse(entry.location).address.split(', ')

                if len(alt_names) > 4:
                    if alt_names[-5] in Constants.known_locations:
                        entry.path = os.path.join(entry.path, alt_names[-5])
                        continue
                if len(alt_names) > 5:
                    if alt_names[-6] in Constants.known_locations:
                        entry.path = os.path.join(entry.path, alt_names[-6])
                        continue
                entry.path = os.path.join(entry.path, default_name)

    def update_names(self,
                     destination_folder: str = "",
                     catalog_entry: bool = False,
                     name_from_captured_date: bool = False,
                     name_from_modified_date: bool = False,
                     keep_manual_names: bool = False) -> None:
        for entry in self.file_list:
            Folder.set_name(entry,
                            destination_folder=destination_folder,
                            catalog_entry=catalog_entry,
                            name_from_captured_date=name_from_captured_date,
                            name_from_modified_date=name_from_modified_date,
                            keep_manual_names=keep_manual_names)

    @staticmethod
    def set_name(entry,
                 destination_folder: str = "",
                 catalog_entry: bool = False,
                 name_from_captured_date: bool = False,
                 name_from_modified_date: bool = False,
                 keep_manual_names: bool = False) -> None:

        if destination_folder:
            entry.path = destination_folder
        if catalog_entry:
            entry.catalog = catalog_entry

        name, ext = os.path.splitext(entry.name)
        if name_from_modified_date and hasattr(entry, "modified"):
            # modification time is only informative so much. Sometimes more info may be extracted later from
            # the original name, so append / keep it.
            entry.name = entry.modified_time_str + '@' + name + ext.lower()
        if (name_from_captured_date or name_from_modified_date) and hasattr(entry, "captured"):
            # if there is a captured date/time, use that, also for modification given
            entry.name = entry.captured_str + ext.lower()
        if keep_manual_names:
            # if there is significant text in the name already, keep that text, ignore numerals
            chars_only = "".join([
                c
                for c in name
                if ('A' <= c <= 'z') or c == ' '
            ])
            if len(chars_only)/len(name) > 0.5:
                if hasattr(entry, "captured"):
                    # but append the captured time to the text if there is one
                    entry.name += name + ' ' + entry.captured_str + ext.lower()
            elif hasattr(entry, "captured"):
                entry.name = entry.captured_str + ext.lower()

