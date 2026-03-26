from flask import Flask, render_template, request, redirect, session
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "secret123"

db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="expense_tracker"
)
cursor = db.cursor()

@app.route('/')
def home():
    return render_template("index.html")

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = generate_password_hash(request.form['password'])

        cursor.execute("INSERT INTO users (name,email,password) VALUES (%s,%s,%s)", (name,email,password))
        db.commit()
        return redirect('/login')
    return render_template("register.html")

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        cursor.execute("SELECT * FROM users WHERE email=%s",(email,))
        user = cursor.fetchone()

        if user and check_password_hash(user[3], password):
            session['user_id'] = user[0]
            return redirect('/dashboard')

    return render_template("login.html")

@app.route('/dashboard', methods=['GET','POST'])
def dashboard():
    if 'user_id' not in session:
        return redirect('/login')

    if request.method == 'POST':
        amount = request.form['amount']
        category = request.form['category']

        cursor.execute("INSERT INTO expenses (user_id,amount,category) VALUES (%s,%s,%s)",
                       (session['user_id'],amount,category))
        db.commit()

    cursor.execute("SELECT * FROM expenses WHERE user_id=%s",(session['user_id'],))
    data = cursor.fetchall()

    cursor.execute("SELECT SUM(amount) FROM expenses WHERE user_id=%s",(session['user_id'],))
    total = cursor.fetchone()[0]

    return render_template("dashboard.html", data=data, total=total)

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

if __name__ == "__main__":
    app.run(debug=True)
