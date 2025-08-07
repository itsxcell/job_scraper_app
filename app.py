from flask import Flask, render_template, request, send_file, redirect, url_for, session, flash
from scraper import scrape_jobs
import os

app = Flask(__name__)
app.secret_key = 'very_secret_key_123'  # Used for sessions — keep it secret in real apps

EXCEL_PATH = os.path.join(os.getcwd(), "static", "jobs.xlsx")

# Hardcoded login credentials
ADMIN_USERNAME = 'admin'
ADMIN_PASSWORD = 'supersecret'

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session['logged_in'] = True
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/', methods=['GET', 'POST'])
def index():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    if request.method == 'POST':
        course_title = request.form['course_title']
        page_num = request.form['page_num']
        jobs = scrape_jobs(course_title, page_num, EXCEL_PATH)
        return render_template('results.html', jobs=jobs, excel_available=os.path.exists(EXCEL_PATH))
    return render_template('index.html')

@app.route('/download')
def download_excel():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    return send_file(EXCEL_PATH, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
