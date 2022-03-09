import unittest
from scraper import *
import pandas as pd


class TestClass(unittest.TestCase):
    def setUp(self):
        self.course_urls = [
            'https://canvas.oregonstate.edu/courses/1792599/assignments/syllabus',  # cs290
            'https://canvas.oregonstate.edu/courses/1798831/assignments/syllabus',  # cs344
            'https://canvas.oregonstate.edu/courses/1784208/assignments/syllabus',  # cs340
            'https://canvas.oregonstate.edu/courses/1780220/assignments/syllabus',  # cs162
            'https://canvas.oregonstate.edu/courses/1738821/assignments/syllabus',  # cs161
            'https://canvas.oregonstate.edu/courses/1830291/assignments/syllabus',  # cs372
            'https://canvas.oregonstate.edu/courses/1772429/assignments/syllabus',  # cs225
            'https://canvas.oregonstate.edu/courses/1764380/assignments/syllabus',  # cs261
            'https://canvas.oregonstate.edu/courses/1806262/assignments/syllabus',  # cs271
            'https://canvas.oregonstate.edu/courses/1784199/assignments/syllabus'  # cs325
        ]

    def test_validator(self):
        # valid URL that doesn't point to a Canvas syllabus page should return False
        valid_url = check_if_url_is_valid('https://www.google.com/')
        self.assertFalse(valid_url)

    def test_validator2(self):
        # valid URL that points to a Canvas home page (not syllabus) should return False
        valid_url = check_if_url_is_valid(
            'https://canvas.oregonstate.edu/courses/1849691')
        self.assertFalse(valid_url)

    def test_validator3(self):
        # valid Canvas syllabus URL should return True
        valid_url = check_if_url_is_valid(
            'https://canvas.oregonstate.edu/courses/1849691/assignments/syllabus')
        self.assertTrue(valid_url)

    def test_validator4(self):
        # valid (non-OSU) Canvas syllabus URL should return True
        valid_url = check_if_url_is_valid(
            'https://canvas.northwestern.edu/courses/7060/assignments/syllabus')
        self.assertTrue(valid_url)

    def test_all_osu_courses(self):
        # verify that the scraped df for each course matches the expected format
        for course_url in self.course_urls:
            syllabus = get_syllabus_content(course_url)
            course_name = get_course_name(syllabus)
            df = convert_syllabus_to_df(syllabus)
            expected_df = pd.read_csv(f'./df/{course_name}_df.csv')
            self.assertTrue(df.equals(expected_df))


if __name__ == '__main__':
    unittest.main(verbosity=2)
