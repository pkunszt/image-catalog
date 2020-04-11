import unittest


class TestDeduplicateDirectories(unittest.TestCase):
    testIndex = 'test_unit_deduplicate_directories'

    def test_find_duplicates(self):
        from deduplicate_directories import DeduplicateDirectories
        deduplicate = DeduplicateDirectories()

        self.fail()

    def test_check_date_name(self):
        from deduplicate_directories import DeduplicateDirectories
        deduplicate = DeduplicateDirectories()
        self.assertTrue(deduplicate.check_date_name('2008-08-16 13-45-01.jpg'))
        self.assertFalse(deduplicate.check_date_name('2008-08-16 13-45-01 (1).jpg'))
        self.assertFalse(deduplicate.check_date_name('P3237432.jpg'))
        self.assertFalse(deduplicate.check_date_name('2008-08-16 13-45-01 2343.jpg'))

    def test_select_name_no_date(self):
        from deduplicate_directories import DeduplicateDirectories
        deduplicate = DeduplicateDirectories()
        item1 = {'id': '1234', 'name': 'Aaaa'}
        item2 = {'id': '132', 'name': 'Bbbb'}
        item3 = {'id': '2345', 'name': 'Cccc'}
        item4 = {'id': '333', 'name': 'Dddd'}
        item5 = {'id': '666', 'name': 'Eeee'}
        example_list = [item3, item1, item2, item4, item5]

        self.assertEqual(deduplicate.select_name_to_keep(example_list), item1)

    def test_select_name_with_date(self):
        from deduplicate_directories import DeduplicateDirectories
        deduplicate = DeduplicateDirectories()
        item1 = {'id': '1234', 'name': 'Aaaa'}
        item2 = {'id': '132', 'name': 'Bbbb'}
        item3 = {'id': '2345', 'name': '2008-08-16 13-45-01.jpg'}
        item4 = {'id': '333', 'name': 'Dddd'}
        item5 = {'id': '666', 'name': '2008-08-16 13-45-01 (1).jpg'}
        example_list = [item5, item1, item2, item3, item4]

        self.assertEqual(deduplicate.select_name_to_keep(example_list), item3)


if __name__ == '__main__':
    unittest.main()
