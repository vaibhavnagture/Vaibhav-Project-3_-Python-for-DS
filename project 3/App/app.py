from flask import Flask, render_template, request, session, redirect
from flask_sqlalchemy import SQLAlchemy
import pickle

import pymysql

app = Flask(__name__)
app.secret_key = '100'
app.app_context().push()

model = pickle.load(open('model.pkl', 'rb'))

pymysql.install_as_MySQLdb()
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:userroot@localhost/loan_prediction'

db = SQLAlchemy(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)


db.create_all()


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username).first()
        if user:
            return render_template('error_register.html')

        new_user = User(username=username, password=password)
        db.session.add(new_user)
        db.session.commit()

        return redirect('/login')

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username, password=password).first()
        if user:
            session['username'] = user.username
            return redirect('/enter_details')
        else:
            return render_template('error_login.html')

    return render_template('login.html')


@app.route('/enter_details', methods=['GET', 'POST'])
def enter_details():
    if 'username' not in session:
        return redirect('/login')

    if request.method == 'POST':
        gender = request.form['gender']
        married = request.form['married']
        dependents = request.form['dependents']
        self_employed = request.form['self_employed']
        education = request.form['education']
        applicant_income = int(request.form['applicant_income'])
        coapplicant_income = int(request.form['coapplicant_income'])
        loan_amount = int(request.form['loan_amount'])
        loan_amount_term = int(request.form['loan_amount_term'])
        credit_history = int(request.form['credit_history'])
        property_area = request.form['property_area']

        input_data = [[gender, married, dependents, education, self_employed, applicant_income,
                       coapplicant_income, loan_amount, loan_amount_term, credit_history, property_area]]

        prediction = model.predict(input_data)
        if prediction > 0.5:
            prediction = "Congratulations! You’re eligible for this loan"

        else:
            prediction = "Sorry, You're not eligible for this loan"

        return render_template('predict.html', prediction=prediction)

    return render_template('predict.html')


@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect('/')


@app.route('/')
def home():
    return render_template('home.html')


if __name__ == '__main__':
    app.run(debug=True)
