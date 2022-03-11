from flask import Flask, Response, redirect, render_template, request, session, url_for
from dotenv import load_dotenv
from scraper import *

app = Flask(__name__)
load_dotenv()
app.secret_key = os.environ.get("SECRET_KEY")


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

        valid_url = check_if_url_is_valid(course_url)
        if not valid_url:
            return render_template('form.html', invalid_url=True)
        syllabus = get_syllabus_content(course_url)
        valid_syllabus = validate_content(syllabus)
        if not valid_syllabus:
            return render_template('form.html', error=True)
        course_name = get_course_name(syllabus)
        df = convert_syllabus_to_df(syllabus)

        if tms == 'Todoist':
            tms_df = process_df_for_todoist(df)
        elif tms == 'Asana':
            tms_df = process_df_for_asana(df)

        session['df'] = tms_df.to_json()  # serialize df
        return render_template('download.html', tms=tms, course_url=course_url, course_name=course_name)


@app.route("/download")
def download():
    df = session.get('df')
    if df:
        df = pd.read_json(df)
        return Response(
            df.to_csv(),
            mimetype="text/csv",
            headers={"Content-disposition":
                     "attachment; filename=syllabus_tasks.csv"})
    else:
        return redirect(url_for('home'))


if __name__ == "__main__":
    app.run()
