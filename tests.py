import unittest
from scraper import *
import pandas as pd
from bs4 import BeautifulSoup


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

    def test_scraper_timeout(self):
        # get_syllabus_content should return None if the URL doesn't contain the expected Canvas syllabus content
        syllabus = get_syllabus_content(
            'https://github.com/jasminjohal/canvas-syllabus-scraper/tree/master/base')
        self.assertIsNone(syllabus)
        # validate_content should return False if passed content is not actually Canvas syllabus content
        valid_syllabus = validate_content(syllabus)
        self.assertFalse(valid_syllabus)

    def test_scraper(self):
        syllabus = get_syllabus_content(
            'https://canvas.oregonstate.edu/courses/1792599/assignments/syllabus')
        if syllabus:
            syllabus_container = syllabus.find(
                'div', {'id': 'syllabusContainer'})
            self.assertIsNotNone(syllabus_container)

    def test_course_name(self):
        # get_course_name should return the correct course name
        with open('testing/html/OPERATING SYSTEMS I (CS_344_400_W2021).html', encoding="utf8") as fp:
            syllabus = BeautifulSoup(fp, 'html.parser')
        course_name = get_course_name(syllabus)
        self.assertEqual(
            course_name, 'OPERATING SYSTEMS I (CS_344_400_W2021)')

    def test_converter_for_all_osu_courses(self):
        # verify that the scraped df for each course matches the expected format
        for course_url in self.course_urls:
            syllabus = get_syllabus_content(course_url)
            course_name = get_course_name(syllabus)
            print(f"Testing {course_name}...")
            df = convert_syllabus_to_df(syllabus)
            # keep_default_na interprets empty cells as empty strings
            expected_df = pd.read_csv(
                f'./testing/df/{course_name}_df.csv', keep_default_na=False)

            self.assertTrue(df.equals(expected_df))


if __name__ == '__main__':
    # unittest.main(verbosity=2)
    unittest.main()
