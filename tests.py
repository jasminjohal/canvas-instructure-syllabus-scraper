import unittest
from scraper import *
import pandas as pd
from bs4 import BeautifulSoup
from dotenv import load_dotenv
load_dotenv()


class TestClass(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
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

    def test_is_canvas_page(self):
        # 'https://github.com/jasminjohal/canvas-instructure-syllabus-scraper/tree/master/base' is technically
        # a valid URL because it contains 'canvas' and 'syllabus' but # is_canvas_page should return False
        # since it is not actually a Canvas page
        with open('testing/html/github.html', encoding="utf8") as fp:
            html = BeautifulSoup(fp, 'html.parser')

        self.assertFalse(is_canvas_page(html))

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
        # allow for os date format discrepancies (Todoist will be fine with either format)
        first_value_in_date_column = df['DATE'].iat[0]
        self.assertTrue(
            first_value_in_date_column == 'Fri Dec 3, 2021 @ 11:59pm' or first_value_in_date_column == 'Fri Dec 03, 2021 @ 11:59pm')

    def test_format_date_column_asana(self):
        # format_date_column should appropriately modify the date column depending on task management system
        df = TestClass.df.copy()
        df = df.rename(columns={'Dates': 'Due Date'})
        format_date_column(df, 'asana')
        first_value_in_date_column = df['Due Date'].iat[0]
        self.assertEqual(first_value_in_date_column, '12/03/2021')


if __name__ == '__main__':
    unittest.main()  # add verbosity=2 argument for more detail
