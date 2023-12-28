from flask import Flask, render_template, redirect, url_for, request, jsonify
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user

import os
from datetime import datetime
from dotenv import load_dotenv

from bokeh.embed import server_document

from emailHandler import send_email
from temperature import read_temp
from loginHandler import checkReq
from logger import writeLog, getLog
from db import writeTemp, checkUserNumber, insertUser, getUser, getUserByID, getConfig, getMinMaxEmail, setConfig

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get("SECRET_KEY")


login_manager = LoginManager()
login_manager.init_app(app)

script, div = None, None
last_known_temp = read_temp()
temp_data = {None}
first_boot = checkUserNumber()
minEmail, maxEmail = getMinMaxEmail()


class User(UserMixin):
    def __init__(self, id, username, email, password):
            self.id = id
            self.username = username
            self.email = email
            self.password = password
    
    @staticmethod
    def get(user_id):
        user_info = getUserByID(user_id)
        if user_info:
            return User(id=user_info[0], username=user_info[1], email=user_info[2], password=user_info[3])
        return None


@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)

@app.route('/')
def main():
    return redirect(url_for('skydelis'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    global first_boot
    if first_boot:
        if request.method == 'POST':
                username = request.form.get('username') 
                email = request.form.get('email')
                password = request.form.get('password')

                message = checkReq(username, email, password)

                if message:
                    return render_template('register.html', error=message)
                else:
                    insertUser(email, password, username)
                    first_boot = False
                    return redirect(url_for('login'))
                

        return render_template('register.html')
    else:
        return render_template('login.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    print(first_boot)
    if not first_boot:
        if current_user.is_authenticated:
            return redirect(url_for('skydelis'))

        if request.method == 'POST':
            email = request.form.get('email')
            password = request.form.get('password')

            message = checkReq(email, password)

            if message:
                return render_template('register.html', error=message)
            else:
                user_id = getUser(email, password)
                if user_id:
                    user = User.get(user_id)
                    if user:
                        login_user(user)
                        return redirect(url_for('skydelis'))
                    
    
            return render_template('login.html', error='Invalid email or password')
        return render_template('login.html')
    else:
        return redirect(url_for('register'))

@app.route('/skydelis')
@login_required
def skydelis():
    global refresh
    script = server_document("http://localhost:5006/bokeh_app")

    logData = getLog()
    config = getConfig()


    return render_template(
        'skydelis.html', 
        script = script, 
        last_known_temp = last_known_temp,
        logData = logData if logData else "",
        email = current_user.email,
        username = current_user.username,
        tempFreq = config[0],
        mixFreq = config[1],
        MailTempMin = '0' if config[2] == 0 else config[2],
        MailTempMax = '0' if config[3] == 0 else config[3]    
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
    
    writeLog(MeasurementTime, current_temp)

    temp_data = {MeasurementTime: current_temp}

    writeTemp(MeasurementTime, current_temp)

    emailHandler(current_temp, MeasurementTime)

    return jsonify(current_temp)

def emailHandler(current_temp, mTime):
    if minEmail == 0.0 and maxEmail == 0.0:
        return
    if maxEmail == 0.0:
        if current_temp < minEmail:
            #send email
            send_email(current_temp, minEmail, mTime, "under")
            return
        else:
            return
    else:
        if current_temp > maxEmail:
            #send email
            send_email(current_temp, maxEmail, mTime, "over")
            return
        else:
            return
    

@app.route('/api/set-temperature', methods=['GET'])
def set_temperature():
    global temp_data
    print(temp_data)
    return jsonify(temp_data)

def is_number(value):
    try:
        float(value)  # Try converting the string to a float
        return True
    except ValueError:
        return False

@app.route('/settings', methods=['POST']) 
def settings():
    global refresh, maxEmail, minEmail
    setting_values = request.form.to_dict()

    password = setting_values['password']
    
    if setting_values['password'] == '':
        password = None

    message = checkReq(setting_values['email'], password, setting_values['name'])
    if not message:
        values_to_check = [
            setting_values['measurement_interval'], 
            setting_values['mixing_interval'], 
            setting_values['temperature_min'], 
            setting_values['temperature_max']
        ]
        # Check if the values, which should be numbers are really numbers
        if all(is_number(value) for value in values_to_check):
            setConfig(setting_values)
            minEmail = float(setting_values['temperature_min'])
            maxEmail = float(setting_values['temperature_max'])
        else:
            return "A value was not a number!", 500
    else:
        return message, 500

    return "OK", 200


if __name__ == '__main__':
    app.run(debug=True, host = "0.0.0.0", port = 5000)
