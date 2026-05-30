from flask import Flask, render_template, request, redirect
import sqlite3
from datetime import datetime
from groq import Groq
import os

app = Flask(__name__)

# GROQ API CONFIGURATION


client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)


# DATABASE 

def init_db():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS patients(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        full_name TEXT NOT NULL,
        dob TEXT NOT NULL,
        email TEXT NOT NULL,
        glucose REAL NOT NULL,
        haemoglobin REAL NOT NULL,
        cholesterol REAL NOT NULL,
        remarks TEXT
    )
    """)

    conn.commit()
    conn.close()

init_db()


# AI Health Prediction

def generate_health_prediction(glucose, haemoglobin, cholesterol):

    prompt = f"""
    You are a healthcare assistant.

    Patient Blood Test Results:
    Glucose: {glucose}
    Haemoglobin: {haemoglobin}
    Cholesterol: {cholesterol}

    Return ONLY:

    Risk Level:
    Possible Condition:
    Remark:

    Keep response under 120 words.
    """

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        return response.choices[0].message.content[:200]

    except Exception as e:
        return f"AI Error: {str(e)}"


# Home Page

@app.route('/')
def home():

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM patients")
    patients = cursor.fetchall()

    conn.close()

    return render_template(
        "index.html",
        patients=patients
    )


# Create

@app.route('/add', methods=['POST'])
def add():

    full_name = request.form['full_name']
    dob = request.form['dob']
    email = request.form['email']
    glucose = request.form['glucose']
    haemoglobin = request.form['haemoglobin']
    cholesterol = request.form['cholesterol']

    # Email Validation
    if '@' not in email:
        return "Invalid Email Address"

    # DOB Validation
    dob_date = datetime.strptime(
        dob,
        "%Y-%m-%d"
    ).date()

    if dob_date > datetime.today().date():
        return "Date of Birth cannot be a future date"

    try:
        glucose = float(glucose)
        haemoglobin = float(haemoglobin)
        cholesterol = float(cholesterol)
    except ValueError:
        return "Blood values must be numeric"

    remarks = generate_health_prediction(
        glucose,
        haemoglobin,
        cholesterol
    )

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO patients
    (
        full_name,
        dob,
        email,
        glucose,
        haemoglobin,
        cholesterol,
        remarks
    )
    VALUES (?,?,?,?,?,?,?)
    """,
    (
        full_name,
        dob,
        email,
        glucose,
        haemoglobin,
        cholesterol,
        remarks
    ))

    conn.commit()
    conn.close()

    return redirect('/')


# Edit 

@app.route('/edit/<int:id>')
def edit(id):

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM patients WHERE id=?",
        (id,)
    )

    patient = cursor.fetchone()

    conn.close()

    return render_template(
        "edit.html",
        patient=patient
    )


# Update

@app.route('/update/<int:id>', methods=['POST'])
def update(id):

    full_name = request.form['full_name']
    email = request.form['email']

    glucose = float(request.form['glucose'])
    haemoglobin = float(request.form['haemoglobin'])
    cholesterol = float(request.form['cholesterol'])

    remarks = generate_health_prediction(
        glucose,
        haemoglobin,
        cholesterol
    )

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("""
    UPDATE patients
    SET
        full_name=?,
        email=?,
        glucose=?,
        haemoglobin=?,
        cholesterol=?,
        remarks=?
    WHERE id=?
    """,
    (
        full_name,
        email,
        glucose,
        haemoglobin,
        cholesterol,
        remarks,
        id
    ))

    conn.commit()
    conn.close()

    return redirect('/')


# Delete

@app.route('/delete/<int:id>')
def delete(id):

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM patients WHERE id=?",
        (id,)
    )

    conn.commit()
    conn.close()

    return redirect('/')


if __name__ == "__main__":
    app.run(debug=True)