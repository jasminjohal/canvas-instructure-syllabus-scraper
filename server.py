from flask import Flask, Response, redirect, render_template, request, session, url_for
from dotenv import load_dotenv
from scraper import *

app = Flask(__name__)
load_dotenv()
app.secret_key = os.environ.get('SECRET_KEY')


@app.route('/', methods=['GET', 'POST'])
def scrape():
    if request.method == 'POST':
        course_url = request.form['course_url']
        tms = request.form['tms']

        if not is_valid_url(course_url):
            return render_template('form.html', invalid_url=True)

        html = get_soupified_html(course_url)
        if not is_canvas_page(html):
            return render_template('form.html', error=True)

        course_name = get_course_name(html)
        syllabus = get_syllabus_rows(html)
        df = convert_syllabus_to_df(syllabus)
        tms_df = process_df_for_tms(df, tms.lower())

        session['df'] = tms_df.to_json()  # serialize df
        return render_template('download.html', tms=tms, course_url=course_url, course_name=course_name)
    else:
        return render_template('form.html')


@app.route('/download')
def download():
    df = session.get('df')
    if not df:
        return redirect(url_for('home'))

    df_for_download = pd.read_json(df)
    return Response(
        df_for_download.to_csv(index=False),
        mimetype='text/csv',
        headers={'Content-disposition':
                 'attachment; filename=syllabus_tasks.csv'})


@app.route('/about')
def about():
    return render_template('about.html')


if __name__ == '__main__':
    app.run()
