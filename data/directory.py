import os
import re
from typing import List, Generator
import reverse_geocoder
import geopy
import geopy.exc

import constants
from constants import Constants
from data.factory import Factory, FactoryError
from data.entry import Entry


class Folder:
    """Class to scan a directory and return a list of entries, either image or video"""
    __file_list: List[Entry]
    __invalid_types_found: set
    __valid_types_found: set
    geo: geopy.geocoders.osm.Nominatim = geopy.geocoders.Nominatim(user_agent="my_catalog")
    __name_date: re.Pattern
    __name_date2: re.Pattern
    __path_date: re.Pattern

    def __init__(self):
        self.__file_list = []
        self.__invalid_types_found = set()
        self.__valid_types_found = set()
        if not hasattr(type(self), "__name_date"):
            type(self).__name_date = re.compile('.*(?P<year>2[0-2]\d\d)(?P<mon>[0-1]\d)(?P<day>[0-3]\d).*')
            type(self).__name_date2 = re.compile('.*(?P<year>2[0-2]\d\d)-(?P<mon>[0-1]\d)-(?P<day>[0-3]\d).*')
            type(self).__path_date = re.compile('.*(?P<year>2[0-2]\d\d)/(?P<mon>[0-1]\d)/(?P<day>[0-3]\d).*')

    def read(self, directory_name: str) -> None:
        """Read from a given directory all image and video files.
        The result can be retrieved as a list of data.entry objects,
        as a list of dictionary objects or as the generator with all entries.
        Entries are images or videos, according to data.image and data.video

        :param str directory_name: Name of the full path of the directory to scan.
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
        """Adding an entry based on the path, internal method. Will add to valid or invalid sets the type at hand"""
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
        """Return the list as a generator to be iterated through immediately"""
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

    def save_paths(self, check: bool = False):
        """Call the save_path method of :class:`Entry` for each entry in our file list."""
        for entry in self.file_list:
            entry.save_path()
            entry.check_if_in_catalog = check

    def update_name_from_location(self):
        """In the given list resolve the city and append the location city to the filename"""
        for entry in self.file_list:
            if entry.location:
                lat, lon = entry.location.split(',')
                default_city = Folder.clean_name(reverse_geocoder.search([(float(lat), float(lon))])[0]['name'])
                alt_city = []
                try:
                    alt_city = Folder.geo.reverse(entry.location, timeout=60).address.split(', ')
                except geopy.exc.GeocoderTimedOut as e:
                    print(f"Timeout on GeoLookup for {entry.location} of {entry.name}. Found {default_city} already.")
                    raise FactoryError("Exiting.")

                name, ext = os.path.splitext(entry.name)
                known_city = ""
                if len(alt_city) > 4:
                    known_city = Folder.get_known_city(alt_city[-5])
                if not known_city and len(alt_city) > 5:
                    known_city = Folder.get_known_city(alt_city[-6])
                if not known_city:
                    known_city = Folder.get_known_city(default_city)
                if known_city:
                    entry.name = name + ' ' + known_city + ext
                    continue

                entry.name = name + ' ' + default_city + ext

    @staticmethod
    def clean_name(name: str) -> str:
        if '/' in name:
            name = name.replace('/', '-')
        if '\\' in name:
            name = name.replace('\\', '-')
        return name

    @staticmethod
    def get_known_city(name: str) -> str:
        for n in Constants.known_locations:
            if name.startswith(n):
                return n
        return ""

    def update_video_path(self):
        """In the given list 'move' the movies into 'filmchen' folder """
        for entry in self.file_list:
            if entry.kind == Constants.VIDEO_KIND and not entry.path.endswith('filmchen'):
                entry.path = os.path.join(entry.path, 'filmchen')

    def update_names(self,
                     destination_folder: str = "",
                     nas: bool = False,
                     dropbox: bool = False,
                     name_from_modified_date: bool = False,
                     keep_manual_names: bool = False,
                     is_month: bool = False) -> None:
        """Call set_name for every name. See set_name."""
        for entry in self.file_list:
            Folder.set_name(entry,
                            destination_folder=destination_folder,
                            nas=nas,
                            dropbox=dropbox,
                            name_from_modified_date=name_from_modified_date,
                            keep_manual_names=keep_manual_names,
                            is_month=is_month)

    @staticmethod
    def set_name(entry: Entry,
                 destination_folder: str = "",
                 nas: bool = False,
                 dropbox: bool = False,
                 name_from_modified_date: bool = False,
                 keep_manual_names: bool = False,
                 is_month: bool = False) -> None:
        """ Set the name and path for a file based on the following criteria:

        Path: if the destination_folder parameter is not empty, use that as the path. If it is empty, assemble the path
        from the captured date (YYYY/MM_MonthName) or if the captured date is not set, from the modified time date.
        Sometimes the filename itself contains a string YYYYMMDD somewhere in the middle (true for Whatsapp images),
        if that pattern is found, set the path accordingly. The name is kept as is.
        However, if the date does not come from the captured time, check that the file has not already been catalogued
        somewhere else and moved there manually. So if the catalog contains the same checksum already, the file is
        skipped.

        Name:
        If the name_from_captured_date is True, and the entry has the captured time, use that to set the file name.
        If the name_from_modified_date is True, and it does have the captured_date, then again the captured date is set.
        Otherwise the modified date is set, prepended to the previous name (with an @ in between).
        There is also a keep_manual_names flag, if set, we simply keep the name if it seems to be mostly characters,
        not digits, because that seems like a human set the name manually.
         """

        if nas:
            entry.nas = True
        if dropbox:
            entry.dropbox = True

        # set folder
        if destination_folder and not is_month:
            entry.path = destination_folder
        else:
            Folder.set_path_from_name(entry)

        # set name
        name, ext = os.path.splitext(entry.name)
        entry.name = name + ext.lower()
        if keep_manual_names and Folder.is_probably_text(name):
            # if there is significant text in the name already, keep that text, ignore numerals
            if hasattr(entry, "captured"):
                # but append the captured time to the text if there is one
                entry.name = name + ' ' + entry.captured_str + ext.lower()
            return
        if hasattr(entry, "captured"):
            # if there is a captured date/time, use that, always
            entry.name = entry.captured_str + ext.lower()
        elif name_from_modified_date:
            # Prepend the modification date if explicitly requested
            entry.name = entry.modified_time_str + ' @ ' + name + ext.lower()

    @staticmethod
    def is_probably_text(name):
        chars_only = "".join([
            c
            for c in name
            if ('A' <= c <= 'z') or c == ' '
        ])
        return len(chars_only) / len(name) > 0.5

    @staticmethod
    def path_from_name(name) -> str:
        n1 = Folder.__name_date.match(name)
        if n1:
            year = n1.group('year')
            month = n1.group('mon')
            return os.path.join(year, constants.get_month_by_number(month))

        n2 = Folder.__name_date2.match(name)
        if n2:
            year = n2.group('year')
            month = n2.group('mon')
            return os.path.join(year, constants.get_month_by_number(month))

        return ""

    @staticmethod
    def path_from_path(entry) -> bool:
        n = Folder.__path_date.match(entry.path)
        if n:
            year = n.group('year')
            month = n.group('mon')
            day = n.group('day')
            entry.path = os.path.join(year, constants.get_month_by_number(month), "Whatsapp")
            entry.name = year + "-" + month + "-" + day + "." + entry.type
            return True
        return False

    @staticmethod
    def set_path_from_name(entry):
        if hasattr(entry, "captured"):
            entry.set_path_from_captured_time()
        else:
            entry.check_if_in_catalog = True
            path = Folder.path_from_name(entry.name)
            if path:
                entry.path = os.path.join(path, "Whatsapp")
                return  # do not modify the name if we got the path from it
            else:
                if Folder.path_from_path(entry):
                    return

            entry.set_path_from_modified_time()

    def print_folders(self):
        paths = dict()
        for item in self.__file_list:
            n = paths.setdefault(item.path, 0)
            paths[item.path] += 1
        for path in paths.keys():
            print(f"{path} : Intention to add {paths[path]} files")
