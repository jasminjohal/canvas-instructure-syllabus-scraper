from flask import Flask, Response
from scraper import get_syllabus_content, convert_syllabus_to_df, process_df_for_todoist
import json

app = Flask(__name__)


@app.route("/")
def hello_world():
    return '<p>CS 361 ID: 1877222</p><p>CS 372 ID: 1830291</p>'


@app.route("/todoist/<int:class_id>")
def todoist(class_id):
    URL = f'https://oregonstate.instructure.com/courses/{class_id}/assignments/syllabus'
    syllabus = get_syllabus_content(URL)
    df = convert_syllabus_to_df(syllabus)
    todoist_df = process_df_for_todoist(df)
    return Response(
        todoist_df.to_csv(),
        mimetype="text/csv",
        headers={"Content-disposition":
                 "attachment; filename=syllabus_for_todoist.csv"})


if __name__ == "__main__":
    app.run()
