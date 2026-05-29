from flask import Flask, render_template, request, redirect
import sqlite3

app = Flask(__name__)

# Create database table
def init_db():

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS patients (

            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fullname TEXT,
            dob TEXT,
            email TEXT,
            glucose REAL,
            haemoglobin REAL,
            cholesterol REAL,
            remarks TEXT
        )
    ''')

    conn.commit()
    conn.close()


# Home Page
@app.route('/')
def home():

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM patients")

    patients = cursor.fetchall()

    conn.close()

    return render_template('index.html', patients=patients)


# Add Patient
@app.route('/add', methods=['GET', 'POST'])
def add_patient():

    if request.method == 'POST':

        fullname = request.form['fullname']
        dob = request.form['dob']
        email = request.form['email']
        glucose = request.form['glucose']
        haemoglobin = request.form['haemoglobin']
        cholesterol = request.form['cholesterol']

        # AI Prediction Logic
        if float(glucose) > 140:
            remarks = "High Diabetes Risk"

        elif float(cholesterol) > 240:
            remarks = "High Cholesterol Risk"

        else:
            remarks = "Normal"

        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO patients
            (fullname, dob, email, glucose,
             haemoglobin, cholesterol, remarks)

            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (fullname, dob, email,
              glucose, haemoglobin,
              cholesterol, remarks))

        conn.commit()
        conn.close()

        return redirect('/')

    return render_template('add.html')


# Edit Patient
@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_patient(id):

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    if request.method == 'POST':

        fullname = request.form['fullname']
        dob = request.form['dob']
        email = request.form['email']
        glucose = request.form['glucose']
        haemoglobin = request.form['haemoglobin']
        cholesterol = request.form['cholesterol']

        # AI Prediction Logic
        if float(glucose) > 140:
            remarks = "High Diabetes Risk"

        elif float(cholesterol) > 240:
            remarks = "High Cholesterol Risk"

        else:
            remarks = "Normal"

        cursor.execute('''
            UPDATE patients

            SET
            fullname=?,
            dob=?,
            email=?,
            glucose=?,
            haemoglobin=?,
            cholesterol=?,
            remarks=?

            WHERE id=?
        ''', (fullname, dob, email,
              glucose, haemoglobin,
              cholesterol, remarks, id))

        conn.commit()
        conn.close()

        return redirect('/')

    cursor.execute("SELECT * FROM patients WHERE id=?", (id,))
    patient = cursor.fetchone()

    conn.close()

    return render_template('edit.html', patient=patient)


# Delete Patient
@app.route('/delete/<int:id>')
def delete_patient(id):

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    cursor.execute("DELETE FROM patients WHERE id=?", (id,))

    conn.commit()
    conn.close()

    return redirect('/')


if __name__ == '__main__':

    init_db()
    app.run(debug=True)