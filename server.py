from flask import Flask, Response, render_template, request
from scraper import *

app = Flask(__name__)

courses = {}
last_processed = None


@app.route("/")
def home():
    return render_template('form.html')


@app.route("/about")
def about():
    return render_template('about.html')


@app.route("/", methods=['POST'])
def todoist():
    if request.method == 'POST':
        course_url = request.form['course_url']
        tms = request.form['tms']

        if course_url not in courses:
            valid_url = check_if_url_is_valid(course_url)
            if not valid_url:
                return render_template('form.html', error=True)
            courses[course_url] = {}
            syllabus = get_syllabus_content(course_url)
            course_name = get_course_name(syllabus)
            df = convert_syllabus_to_df(syllabus)
            courses[course_url]['raw'] = df
            courses[course_url]['name'] = course_name

        if tms not in courses[course_url]:
            df = courses[course_url]['raw']
            if tms == 'Todoist':
                tms_df = process_df_for_todoist(df)
            elif tms == 'Asana':
                tms_df = process_df_for_asana(df)
            courses[course_url][tms] = tms_df

        global last_processed
        last_processed = courses[course_url][tms]

        return render_template('download.html', tms=tms, course_url=course_url, course_name=courses[course_url]['name'])


@app.route("/download")
def download():
    return Response(
        last_processed.to_csv(),
        mimetype="text/csv",
        headers={"Content-disposition":
                 "attachment; filename=syllabus_tasks.csv"})


if __name__ == "__main__":
    app.run()
