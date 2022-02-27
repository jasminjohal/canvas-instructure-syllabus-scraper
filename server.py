from flask import Flask, Response
from scraper import get_syllabus_content, convert_syllabus_to_df, process_df_for_todoist
import json

app = Flask(__name__)


@app.route("/")
def hello_world():
    return '<h1>Hello world!</h1>'


@app.route("/todoist")
def todoist():
    CS361_URL = 'https://oregonstate.instructure.com/courses/1877222/assignments/syllabus'
    # CS372_URL = 'https://oregonstate.instructure.com/courses/1830291/assignments/syllabus'
    syllabus = get_syllabus_content(CS361_URL)
    df = convert_syllabus_to_df(syllabus)
    todoist_df = process_df_for_todoist(df)
    return Response(
        todoist_df.to_csv(),
        mimetype="text/csv",
        headers={"Content-disposition":
                 "attachment; filename=syllabus_for_todoist.csv"})
