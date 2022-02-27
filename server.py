from flask import Flask
from scraper import get_syllabus_content, convert_syllabus_to_df
import json

app = Flask(__name__)


@app.route("/")
def hello_world():
    CS361_URL = 'https://oregonstate.instructure.com/courses/1877222/assignments/syllabus'
    # CS372_URL = 'https://oregonstate.instructure.com/courses/1830291/assignments/syllabus'
    syllabus = get_syllabus_content(CS361_URL)
    df = convert_syllabus_to_df(syllabus)
    return '<p>testing</p>'
