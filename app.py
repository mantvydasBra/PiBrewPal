import os
from db import writeTemp
from datetime import datetime
from dotenv import load_dotenv
from temperature import read_temp
from bokeh.embed import server_document, server_session, components
from bokeh.client import pull_session
from flask import Flask, render_template, redirect, url_for, request, jsonify
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import pandas as pd
# from bokeh_app import source, newTemp
# from bokeh_app import newTemp

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get("SECRET_KEY")
# session = pull_session(session_id=None, url='http://localhost:5006/bokeh_app')
# app_url = 'http://localhost:5006/bokeh_app'
# mysession = pull_session(url=app_url)

login_manager = LoginManager()
login_manager.init_app(app)

script, div = None, None
last_known_temp = 0
temp_data = {None}


class User(UserMixin):
    def __init__(self, id, email, password):
            self.id = id
            self.email = email
            self.password = password


users = {
    1: User(1, 'admin@admin.net', '1234'),
    2: User(2, 'user@user.com', '4321'),
}

@login_manager.user_loader
def load_user(user_id):
    return users.get(int(user_id))

@app.route('/')
def main():
    return redirect(url_for('skydelis'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('skydelis'))

    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = next((user for user in users.values() if user.email == email), None)

        if user is not None and user.password == password:
            login_user(user)
            return redirect(url_for('skydelis'))
        
        
        return render_template('login.html', error='Invalid email or password')


    return render_template('login.html')

@app.route('/skydelis')
@login_required
def skydelis():
    # app_url = 'http://localhost:5006/'
    # with pull_session(url=app_url) as mysession:
    with pull_session(session_id=None, url='http://localhost:5006/bokeh_app') as session:
    # script = server_document(url='http://localhost:5006/bokeh_app')
    
    # doc = session.document
    # print(source.data)
        
    # script = server_document('http://localhost:5006/bokeh_app')
        script = server_session(session_id=session.id, url = "http://localhost:5006/bokeh_app")

        return render_template(
            'skydelis.html', 
            script = script, 
            last_known_temp = last_known_temp,
        )


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))

@login_manager.unauthorized_handler
def unauthorized_callback():
    return redirect(url_for('login'))


############### API PART #######################
# Define an API endpoint
@app.route('/api/get-temperature', methods=['GET'])
def get_temperature():
    global last_known_temp, temp_data
    MeasurementTime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    current_temp = read_temp()

    last_known_temp = current_temp

    temp_data = {MeasurementTime: current_temp}
    writeTemp(MeasurementTime, current_temp)

    return jsonify(current_temp)

@app.route('/api/set-temperature', methods=['GET'])
def set_temperature():
    global temp_data
    print(temp_data)
    return jsonify(temp_data)

if __name__ == '__main__':
    app.run(debug=True, host = "0.0.0.0", port = 5000)
