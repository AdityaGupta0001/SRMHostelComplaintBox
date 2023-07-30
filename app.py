from flask import Flask,render_template,redirect,url_for,session,request,flash,jsonify
from flask_pymongo import PyMongo
import secrets

app = Flask(__name__)

app.config['MONGO_URI']= "mongodb://localhost:27017/flask_login_signup"
app.secret_key =  secrets.token_hex(16)
mongo=PyMongo(app)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = mongo.db.users.find_one({'email': email})
        if user and user['password'] == password:
            session['user_id'] = str(user['_id'])  
            flash('Login successful!', 'success')
            mongo.db.users.update_one({"email" : user["email"]},{'$set':{"status": "logged-in"}})
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid email or password', 'danger')
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        existing_user = mongo.db.users.find_one({'email': email})
        if existing_user:
            flash('Email already exists. Please log in.', 'warning')
            return redirect(url_for('login'))
        else:
            user_id = mongo.db.users.insert_one({'email': email, 'password': password, 'status':"logged-out"})
            session['user_id'] = str(user_id.inserted_id)  # Store user_id in session
            flash('Account created successfully!', 'success')
            return redirect(url_for('loign'))
    return render_template('signup.html')

@app.route('/home')
def home():
    # You can implement the dashboard or homepage for authenticated users here
    return render_template('home.html')

@app.route('/dashboard')
def dashboard():
    user = mongo.db.users.find_one({'status': "logged-in"})

    if user:
        return render_template('dashboard.html', user_email=user['email'])
    else:
        flash('User not found.', 'danger')
        return redirect(url_for('login'))

@app.route('/logout')
def logout():
    session.clear()  # Clear the session to log out the user
    flash('You have been logged out.', 'info')
    loggedin_user = mongo.db.users.find_one({'status': "logged-in"})
    if loggedin_user:
         mongo.db.users.update_one({"email" : loggedin_user["email"]},{'$set':{"status": "logged-out"}})
    return redirect(url_for('login'))

if __name__=="__main__":
    app.run(debug=True, port =8000)