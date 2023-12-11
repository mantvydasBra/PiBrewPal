import os
import figures
from dotenv import load_dotenv
from bokeh.embed import components
from flask import Flask, render_template, redirect, url_for, request
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get("SECRET_KEY")


login_manager = LoginManager()
login_manager.init_app(app)

script, div = None, None


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
    # Setting variables to global, because otherwise function doesn't see vartiables at the top
    global script, div

    # Making a check to see if components are already generated, to not access same object again and get an error
    if script is None and div is None:
    # Function to calculate the plot
        p, select = figures.drawLinePlot()
    # Save components for displaying to the website
        script, div = components((p, select))

    return render_template(
        'skydelis.html', 
        script = script, 
        div = [div[0], div[1]]
    )

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))

@login_manager.unauthorized_handler
def unauthorized_callback():
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True, host = "0.0.0.0")
