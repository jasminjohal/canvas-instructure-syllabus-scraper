from flask import Flask, Response, render_template, request
from scraper import get_syllabus_content, convert_syllabus_to_df, process_df_for_todoist

app = Flask(__name__)

courses = {}
last_processed = None


@app.route("/")
def home():
    return render_template('index.html')


@app.route("/", methods=['POST'])
def todoist():
    if request.method == 'POST':
        course_url = request.form['course_url']
        tms = request.form['tms']

        if course_url not in courses:
            courses[course_url] = {}
            syllabus = get_syllabus_content(course_url)
            df = convert_syllabus_to_df(syllabus)
            courses[course_url]['raw'] = df

        if tms not in courses[course_url]:
            if tms == 'Todoist':
                tms_df = process_df_for_todoist(df)
            elif tms == 'Asana':
                pass
            courses[course_url][tms] = tms_df

        global last_processed
        last_processed = courses[course_url][tms]

        return render_template('download.html', tms=tms, course_url=course_url)


@app.route("/download")
def download():
    return Response(
        last_processed.to_csv(),
        mimetype="text/csv",
        headers={"Content-disposition":
                 "attachment; filename=syllabus_for_todoist.csv"})


if __name__ == "__main__":
    app.run()
