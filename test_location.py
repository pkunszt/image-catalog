from unittest import TestCase
import reverse_geocode
import reverse_geocoder
import geopy
import csv


class TestLocations(TestCase):
    a: geopy.geocoders.osm.Nominatim

    def setUp(self) -> None:
        type(self).a = geopy.geocoders.Nominatim(user_agent="my_catalog")

    def test_locations(self):
        with open("coord.csv", "r") as file:
            for row in csv.DictReader(file, dialect='excel'):
                self.do_print5(row['lat'], row['lon'])

    @staticmethod
    def do_print(lat, lon):
        print(lat, lon,
              reverse_geocode.search([lat, lon])[0], ":",
              TestLocations.a.reverse(f"{lat},{lon}").address.split(', ')[-5:-4], ":",
              reverse_geocoder.search([(lat, lon)])[0]
              )

    @staticmethod
    def do_print2(lat, lon):
        name1 = reverse_geocoder.search([(lat, lon)])[0]['name']
        print(lat, lon, end=" ")
        if len(name1.split(' ')) > 1:
            name2_list = TestLocations.a.reverse(f"{lat},{lon}").address.split(', ')
            if len(name2_list) > 5:
                name2 = name2_list[-5]
                if len(name2.split(' ')) >= len(name1.split(' ')):
                    print(f"{name1} 1.1    two would be {name2}")
                    return
                print(f"{name2} 2   one would be {name1}")
            else:
                print(f"{name1} 1.2    two would be {name2_list[-4]}")
        else:
            print(f"{name1} 1")

    @staticmethod
    def do_print3(lat, lon):
        name1 = reverse_geocoder.search([(lat, lon)])[0]
        if len(name1['name'].split(' ')) > 1:
            print(f"{name1['admin1']}  2 {name1['name']}")
        else:
            print(f"{name1['name']}  1 {name1['admin1']}")

    @staticmethod
    def do_print4(lat, lon):
        name1 = reverse_geocoder.search([(lat, lon)])[0]
        print(f"1: {name1['name']}", end=" ")
        print(f"2: {name1['admin1']}", end=" ")
        name2_list = TestLocations.a.reverse(f"{lat},{lon}").address.split(', ')
        if len(name2_list) >= 5:
            print(f"3: {name2_list[-5]}", end=" ")
        if len(name2_list) >= 6:
            print(f"4: {name2_list[-6]}")
        else:
            print(" ")

    @staticmethod
    def do_print5(lat, lon):
        known_names = {'Riederalp', 'Le Lignon', 'Zürich', 'Winterthur', 'Los Angeles', 'Barcelona'}
        name1 = reverse_geocoder.search([(lat, lon)])[0]['name']
        name3_4 = TestLocations.a.reverse(f"{lat},{lon}").address.split(', ')
        if len(name3_4) > 4:
            if name3_4[-5] in known_names:
                print (name3_4[-5])
                return
        if len(name3_4) > 5:
            if name3_4[-6] in known_names:
                print(name3_4[-6])
                return
        print(name1)
        return
