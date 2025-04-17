from flask import Flask, render_template, request, redirect, url_for, session
import pandas as pd
import time
from static.additional_functions import *

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # required for session handling

# Paths
CSV_PATH = 'https://docs.google.com/spreadsheets/d/e/2PACX-1vRxhcb6-OxVSZCREHi8Kp7qFu63KS-alr28lBzpm2tbvvLfxb398merZWhuqeKn0hWcbL8t3OU-B6IE/pub?output=csv'
USER_CREDENTIALS = 'static/users/login.csv'


@app.route('/', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        userid = request.form.get('userid')
        password = request.form.get('password')

        # Read users from login.csv
        try:
            users_df = pd.read_csv(USER_CREDENTIALS)
        except Exception as e:
            return f"Error loading user file: {e}"

        # Check if credentials are valid
        match = users_df[(users_df['userid'] == userid) & (users_df['password'] == password)]

        if not match.empty:
            session['user'] = userid  # Set session variable
            return redirect(url_for('data_view'))
        else:
            error = "Invalid credentials. Please try again."

    return render_template('index.html', error=error)


@app.route('/dashboard')
def data_view():
    # Check if user is logged in
    if 'user' not in session:
        return redirect(url_for('login'))

    return load_and_show_data()


def load_and_show_data():
    try:
        df = dataframeSafai(CSV_PATH)

        html = '<table class="table table-striped">'
        html += '<thead><tr>' + ''.join(f'<th>{col}</th>' for col in df.columns) + '</tr></thead>'

        for status, group in df.groupby('scrutiny_status', dropna=False):
            html += '<tbody class="status-group">'
            for _, row in group.iterrows():
                html += '<tr>'
                for col, cell in zip(row.index, row.values):
                    cell_str = str(cell)

                    # Assign class to scrutiny_status cell
                    css_class = ''
                    if col == 'scrutiny_status' and isinstance(cell_str, str):
                        if 'pending' in cell_str.lower():
                            css_class = 'status-pending'
                        elif 'done' in cell_str.lower():
                            css_class = 'status-done'
                        elif 'in process' in cell_str.lower():
                            css_class = 'status-inprocess'

                    html += f'<td class="{css_class}">{cell_str}</td>'
                html += '</tr>'
            html += '</tbody>'

        html += '</table>'
        return render_template('dashboard.html', table=html)

    except Exception as e:
        return f"Error reading data: {e}"

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(debug=True)
