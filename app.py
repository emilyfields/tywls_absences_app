# ---- YOUR APP STARTS HERE ----
# -- Import section --
from flask import Flask
from flask_pymongo import PyMongo

from bson.objectid import ObjectId

from flask import render_template, request, redirect, session, url_for

from datetime import datetime


# -- Initialization section --
app = Flask(__name__)

#secret key for user logins
app.secret_key = '_5#y2L"F4Q8z\n\xec]/'

# name of database
app.config['MONGO_DBNAME'] = 'absences'

# URI of database
app.config['MONGO_URI'] = 'mongodb+srv://admin:changeme123@cluster0-cnobo.mongodb.net/absences?retryWrites=true&w=majority'

mongo = PyMongo(app)

# -- Routes section --

# LOGIN
@app.route('/')
@app.route('/index')
@app.route('/login', methods=['POST', 'GET'])

def login():
    if request.method == 'POST':
        users = mongo.db.teachers
        absences = mongo.db.absences
        coverages = mongo.db.coverages

        login_user = users.find_one({'name': request.form['username']})

        if login_user is None:
            return render_template('index.html', error = 'User does not exist. Sign up to create an account.', time=datetime.now())
        if login_user:
            if request.form['password'] == login_user['password']:
                session['username'] = request.form['username']

                user_absences = list(absences.find({'teacher out': session['username']}))
                user_coverages = list(coverages.find({'covered by': session['username']}))

                return render_template('homepage.html', time=datetime.now(), user = login_user, absences = user_absences, coverages = user_coverages)

        return render_template('index.html', error = 'Invalid username/password combination. Try again', time=datetime.now())

    elif request.method == 'GET':
        return render_template('index.html', time=datetime.now())


#SIGNUP

@app.route('/signup', methods=['POST', 'GET'])

def signup():
    if request.method == 'GET':
        return render_template('signup.html', time=datetime.now())

    elif request.method == 'POST':
        users = mongo.db.teachers
        existing_user = users.find_one({'name' : request.form['username']})

        if existing_user is None:
            # list_of_classes = ['class_one_', 'class_two_', 'class_three_', 'class_four_', 'class_five_']
            # schedule = {
            #     '1':{"class name": "free", "room": "none"},
            #     '2':{"class name": "free", "room": "none"},
            #     '3':{"class name": "free", "room": "none"},
            #     '4':{"class name": "free", "room": "none"},
            #     '5':{"class name": "free", "room": "none"},
            #     '6':{"class name": "free", "room": "none"},
            #     '7':{"class name": "free", "room": "none"},
            #     '8':{"class name": "free", "room": "none"}
            #     }

            # for a_class in list_of_classes:
            #     schedule[str(request.form[a_class+'period'])] = {
            #         "class name": request.form[a_class+'name'],
            #         "room": request.form[a_class+'room']
            #     }

            users.insert({
                'name': request.form['username'], 
                'password': request.form['password'],
            })

            session['username'] = request.form['username']

            return redirect(url_for('homepage'))

        return redirect(url_for('signup'), error = 'You already already exists! Try logging in instead.')


# HOMEPAGE!
@app.route('/homepage/')
@app.route('/homepage')

def homepage():
    users = mongo.db.teachers
    absences = mongo.db.absences
    coverages = mongo.db.coverages
    
    existing_user = list(users.find_one({'name': session['username']}))
    user_absences = list(absences.find({'teacher out': session['username']}))
    user_coverages = list(coverages.find({'covered by': session['username']}))

    return render_template('homepage.html', time=datetime.now(), user = existing_user, absences = user_absences, coverages = user_coverages)



#CREATE ABSENCES
@app.route('/myabsences', methods=['POST', 'GET'])

def create_absence():
    teacher_collection = mongo.db.teachers
    user = teacher_collection.find_one({'name': session['username']})

    absences_collection = mongo.db.absences
    coverages_collection = mongo.db.coverages
    
    if request.method == 'GET':
        return render_template('create_absences.html', user = user)

    elif request.method == 'POST':
        date = request.form['date']
        dateObj = datetime.strptime(date, '%Y-%m-%d')
        dateStr = dateObj.strftime('%b %d, %Y')

        absences_collection.insert({
            'teacher out': user['name'], 
            'date': dateStr,
            'period': request.form['period'],
            'class': request.form['class_name'],
            'room': request.form['room'],
            'coverage': "no"
        })

        absences = list(absences_collection.find({'teacher out': user['name']}))
        coverages = list(coverages_collection.find({'covered by': user['name']}))
        
        return render_template('homepage.html', user = user, absences = absences, coverages = coverages)



#ACCEPT COVERAGES
@app.route('/accept/coverages', methods=['POST', 'GET'])

def accept_coverages():
    teacher_collection = mongo.db.teachers
    user = teacher_collection.find_one({'name': session['username']})

    absences_collection = mongo.db.absences

    coverages_needed = list(absences_collection.find({'coverage': 'no'}).sort('date', 1))
    
    if request.method == 'GET':
        return render_template('accept_coverages.html', user = user, coverages = coverages_needed)

    elif request.method == 'POST':

        absences = list(absences_collection.find({'teacher out': user['name']}))
        coverages = list(coverages_collection.find({'covered by': user['name']}))
        
        return render_template('homepage.html', user = user, absences = absences, coverages = coverages)



#LOGOUT
@app.route('/logout')

def logout():
    session.clear()
    return redirect('/')