import unittest
from scraper import *
import pandas as pd
from bs4 import BeautifulSoup
from dotenv import load_dotenv
load_dotenv()


class TestClass(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.course_urls = [
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

        # create a BeautifulSoup object that contains a single tr element of a syllabus
        with open('testing/html/row_with_date.html', encoding="utf8") as fp:
            soup = BeautifulSoup(fp, 'html.parser')
            cls.row_with_date = soup.tr

        # create a BeautifulSoup object that contains a single tr element of a syllabus
        with open('testing/html/row_without_date.html', encoding="utf8") as fp:
            soup = BeautifulSoup(fp, 'html.parser')
            cls.row_without_date = soup.tr

        # create a dummy syllabus df
        tasks = ['task #1', 'task #2', 'task #3']
        dates = ['Fri Dec 3, 2021', 'Sat Dec 4, 2021', 'Sun Dec 5, 2021']
        times = ['11:59pm', '1:00pm', '6:00pm']
        cls.df = create_df(tasks, dates, times)

    def test_url_validator(self):
        # valid URL that doesn't point to a Canvas syllabus page should return False
        valid_url = is_valid_url('https://www.google.com/')
        self.assertFalse(valid_url)

    def test_url_validator2(self):
        # valid URL that points to a Canvas home page (not syllabus) should return False
        valid_url = is_valid_url(
            'https://canvas.oregonstate.edu/courses/1849691')
        self.assertFalse(valid_url)

    def test_url_validator3(self):
        # valid Canvas syllabus URL should return True
        valid_url = is_valid_url(
            'https://canvas.oregonstate.edu/courses/1849691/assignments/syllabus')
        self.assertTrue(valid_url)

    def test_url_validator4(self):
        # valid (non-OSU) Canvas syllabus URL should return True
        valid_url = is_valid_url(
            'https://canvas.northwestern.edu/courses/7060/assignments/syllabus')
        self.assertTrue(valid_url)

    def test_scraper_timeout(self):
        # get_soupified_html should return None if the URL doesn't contain Canvas syllabus content
        html = get_soupified_html(
            'https://github.com/jasminjohal/canvas-syllabus-scraper/tree/master/base')
        self.assertIsNone(html)
        # is_canvas_page should return False if passed content is not actually Canvas page
        self.assertFalse(is_canvas_page(html))

    def test_scraper(self):
        # every Canvas syllabus page has a div#syllabusContainer that contains the syllabus content
        html = get_soupified_html(
            'https://canvas.oregonstate.edu/courses/1792599/assignments/syllabus')
        if html:
            syllabus_container = html.find(
                'div', {'id': 'syllabusContainer'})
            self.assertIsNotNone(syllabus_container)

    def test_course_name(self):
        # get_course_name should return the correct course name
        with open('testing/html/OPERATING SYSTEMS I (CS_344_400_W2021).html', encoding="utf8") as fp:
            html = BeautifulSoup(fp, 'html.parser')
        course_name = get_course_name(html)
        self.assertEqual(
            course_name, 'OPERATING SYSTEMS I (CS_344_400_W2021)')

    def test_contains_date(self):
        # contains_date should return True if the tr has a class in the format "events_2020_09_27"
        row = TestClass.row_with_date
        self.assertTrue(contains_date(row))

    def test_contains_date2(self):
      # contains_date should return False if the tr does not have a class in the format "events_2020_09_27"
        row = TestClass.row_without_date
        self.assertFalse(contains_date(row))

    def test_extract_date_with_date(self):
        # extract_date should pull the date from an HTML class and convert it
        # to a string in the form '%a %b %#d, %Y'
        task_date = extract_date(TestClass.row_with_date)
        self.assertEqual(task_date, 'Fri Dec 3, 2021')

    def test_extract_date_without_date(self):
        # extract_date should return '' if there is no date class
        task_date = extract_date(TestClass.row_without_date)
        self.assertEqual(task_date, '')

    def test_extract_task_name(self):
        # extract_task_name should pull the task name from a td in a row
        task_name = extract_task_name(TestClass.row_with_date)
        self.assertEqual(task_name, '5.7 - Discussion: Project Showcase')

    def test_extract_time(self):
        # extract_time should pull the raw time from a td in a row
        task_time = extract_time(TestClass.row_with_date)
        self.assertEqual(task_time, 'due by 11:59pm')

    def test_create_df_column_names(self):
        # create_df should have built a df with the correct column names
        self.assertCountEqual(TestClass.df.columns.values, [
                              'Tasks', 'Dates', 'Times'])

    def test_create_df_size(self):
        # create_df should have built a df with the correct number of rows and columns
        num_rows = TestClass.df.shape[0]
        num_columns = TestClass.df.shape[1]
        self.assertEqual(num_rows, 3)
        self.assertEqual(num_columns, 3)

    def test_rename_columns_todoist(self):
        # rename_columns should appropriately change name of df columns
        df = TestClass.df.copy()  # don't overwrite class df
        df = rename_columns(df, 'todoist')
        self.assertCountEqual(df.columns.values, ['CONTENT', 'DATE', 'Times'])

    def test_rename_columns_asana(self):
        # rename_columns should appropriately change name of df columns depending on task management system
        df = TestClass.df.copy()
        df = rename_columns(df, 'asana')
        self.assertCountEqual(df.columns.values, [
                              'Name', 'Due Date', 'Description'])

    def test_add_columns_todoist(self):
        # add_columns should appropriately add colums to df depending on task management system
        df = TestClass.df.copy()
        add_columns(df, 'todoist')
        self.assertCountEqual(df.columns.values, [
                              'Tasks', 'Dates', 'Times', 'TYPE', 'PRIORITY', 'INDENT', 'AUTHOR', 'RESPONSIBLE', 'DATE_LANG', 'TIMEZONE'])

    def test_add_columns_asana(self):
        # add_columns should appropriately add colums to df depending on task management system
        df = TestClass.df.copy()
        add_columns(df, 'asana')
        self.assertCountEqual(df.columns.values, [
                              'Tasks', 'Dates', 'Times', 'Assignee', 'Collaborators', 'Start Date', 'Type', 'Section/Column'])

    def test_format_date_column_todoist(self):
        # format_date_column should appropriately modify the date column depending on task management system
        df = TestClass.df.copy()
        df = df.rename(columns={'Dates': 'DATE'})
        format_date_column(df, 'todoist')
        self.assertEqual(df['DATE'].iat[0], 'Fri Dec 3, 2021 @ 11:59pm')

    def test_format_date_column_asana(self):
        # format_date_column should appropriately modify the date column depending on task management system
        df = TestClass.df.copy()
        df = df.rename(columns={'Dates': 'Due Date'})
        format_date_column(df, 'asana')
        self.assertEqual(df['Due Date'].iat[0], '12/03/2021')

    # def test_converter_for_all_osu_courses(self):
    #     # end-to-end test
    #     # verify that the scraped df for each course matches the expected format
    #     for course_url in TestClass.course_urls:
    #         syllabus = get_syllabus_content(course_url)
    #         course_name = get_course_name(syllabus)
    #         print(f"Testing {course_name}...")
    #         df = convert_syllabus_to_df(syllabus)
    #         # keep_default_na interprets empty cells as empty strings
    #         expected_df = pd.read_csv(
    #             f'./testing/df/{course_name}_df.csv', keep_default_na=False)

    #         self.assertTrue(df.equals(expected_df))


if __name__ == '__main__':
    # unittest.main(verbosity=2)
    unittest.main()
