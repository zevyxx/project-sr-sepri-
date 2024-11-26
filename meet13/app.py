from flask import Flask, render_template, request, session, redirect, url_for
import secrets
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    database="project",
    password=""
)

@app.route('/')
@app.route('/home')
def home():
    if "user" in session:
        username = session["user"]
        return render_template('home.html', username=username, logged_in=True)
    else:
        return render_template('home.html', logged_in=False)

@app.route('/login')
def login():
    if session.get("user"):
        return redirect(url_for("profile"))
    return render_template('login.html')

@app.route('/aksi_login', methods=["POST"])
def aksi_login():
    cursor = mydb.cursor()
    query = "SELECT * FROM user WHERE username = %s AND password = %s"
    data = (request.form['username'], request.form['password'])
    cursor.execute(query, data)
    value = cursor.fetchone()

    if value:
        print(f"Login berhasil: {value}")
        session["user"] = request.form['username']
        return redirect(url_for('profile'))
    else:
        print(f"Login gagal: {request.form['username']}")
        return render_template('login.html', error="Invalid username or password")

@app.route('/profile')
def profile():
    if "user" in session:
        username = session["user"]
        return render_template("profile.html", username=username)
    else:
        return redirect(url_for("login"))

@app.route('/logout')
def logout():
    session.pop("user", None)
    return redirect(url_for("home"))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        cursor = mydb.cursor()
        cursor.execute("SELECT * FROM user WHERE username = %s", (username,))
        existing_user = cursor.fetchone()

        if existing_user:
            return render_template('register.html', error="Username already exists!")

        hashed_password = generate_password_hash(password)
        cursor.execute("INSERT INTO user (username, password) VALUES (%s, %s)", (username, hashed_password))
        mydb.commit()

        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/edit_profile')
def edit_profile():
    if "user" in session:
        return render_template("edit_profile.html")
    else:
        return redirect(url_for('login'))

@app.route('/product_page')
def product_page():
    return render_template("product_page.html")

@app.route('/update_profile', methods=['GET', 'POST'])
def update_profile():
    if "user" not in session:
        return redirect(url_for("login"))
    
    if request.method == 'POST':
        new_username = request.form['username']
        
        cursor = mydb.cursor()
        update_query = """
        UPDATE user 
        SET username = %s
        WHERE username = %s
        """
        cursor.execute(update_query, (new_username, session["user"]))
        mydb.commit()

        session["user"] = new_username
        
        return redirect(url_for('profile'))

    cursor = mydb.cursor()
    cursor.execute("SELECT username FROM user WHERE username = %s", (session["user"],))
    user = cursor.fetchone()

    return render_template('update_profile.html', username=user[0])


if __name__ == "__main__":
    app.run(debug=True)
