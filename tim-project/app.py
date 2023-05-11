import re
from flask import Flask, render_template, request, session, redirect, url_for, flash
from flask_session import Session
from hashlib import sha256
import sys, os
import secrets
import urllib.parse
from urllib.parse import unquote
from datetime import datetime, date
from flask_mail import Mail, Message

"""
Admin perspective
When a form is evaluated (rejected, accepted, redrafted)
- Send email to that student.
Delete a form
"""


# Get the path to the parent directory of this file (i.e., the "project" folder)
project_dir = os.path.dirname(os.path.abspath(__file__))
# Add the path to the "back-end" directory to the Python path
backend_dir = os.path.join(project_dir, 'back-end')
sys.path.append(backend_dir)
from Handshake import HandShake

app = Flask(__name__)
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)
app.config['SECRET_KEY'] = secrets.token_hex(32)
app.config['MAIL_SERVER'] = 'localhost'
app.config['MAIL_PORT'] = 1025  # The default MailHog SMTP port
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USERNAME'] = 'username'
app.config['MAIL_PASSWORD'] = 'password'
app.config['MAIL_DEFAULT_SENDER'] = 're-link-noreply@msmary.re-link.edu'

mail = Mail(app)

def validate_sign_up(first_name, last_name, email, password, confirm_password):
    error = ""
    if not first_name and not last_name and not email and not password and not confirm_password:
        error = 'Please ensure all fields are entered.'

    elif not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        error = 'Please enter a valid email address'
    elif password != confirm_password:
        error = 'Please ensure both passwords entered match.'
    elif len(password) < 8:
        error = 'Please enter a password that is at least 8 characters in length'
    return error

@app.route('/')
def index():
    user_id = session.get('user_id')
    if user_id:
        return render_template('index.html')
    else:
        return redirect(url_for('login'))
    
@app.route('/verify')
def verify():
    user_id = session.get('user_id')
    if user_id:
        return redirect(url_for('index'))
    email = unquote(request.args.get('email', ''))
    code = unquote(request.args.get('code', ''))
    if email and code:
        code_from_session = session.get('register_code')
        user = session.get('user')
        email_from_session = user['student']['email']
        if code_from_session == code and email == email_from_session:
            hs = HandShake("HandshakeDB")
            result = hs.insertStudent(session['user'])
            if result:
                message = "Successfully verified registration. Please click <a href='/login'>Here</a> to login!"
                return render_template('verify.html', success = message)
            else:
                error = "Sorry there was an error with registering your account. Please try again later."
                return render_template('verify.html', error = error)
        else:
            error = "Sorry, Unauthorized access."
            return render_template('verify.html', error = error)
    else:
        error = "Sorry, Unauthorized access."
        return render_template('verify.html', error = error)

@app.route('/editForm', methods=['POST', 'GET'])
def editForm():
    if request.method == 'GET':
        form_id = request.args.get('form_id')
        user_id = session.get('user_id')
        if not user_id:
            return redirect(url_for('login'))
        hs = HandShake("HandshakeDB")
        forms = hs.getStudentForms(user_id)
        valid = False
        i = 0
        for form in forms:
            if form[0] == int(form_id) and (form[7] == 'pending' or form[7] == 'redraft'):
                valid = True
                break
            i += 1
        if valid:
            edit_form = forms[i]
            return render_template('editForm.html', form = edit_form)
        else:
            flash("Sorry, there was an error when attempting to redirect you. Try again later please.")
            return redirect(url_for('status'))
    elif request.method == 'POST':
        user_id = session.get('user_id')
        if not user_id:
            return redirect(url_for('login'))
        event_role = request.form.get('role').split('_')[1].lower()
        event_name = request.form.get('name')
        event_manager = request.form.get('manager')
        event_location = request.form.get('location')
        additional_info = request.form.get('additional_info')
        event_date_str = request.form.get('date')
        event_date = datetime.strptime(event_date_str, '%Y-%m-%d').date()
        event_date_formatted = event_date.strftime('%Y-%m-%d')
        today = date.today()
        if validate_form(event_name, event_location, additional_info):
            if not additional_info:
                additional_info = None
            if not event_manager:
                event_manager = None
            form_id = request.form.get('form_id')
            data = {
                "forms":{
                    "event_role": event_role,
                    "event_name": event_name,
                    "event_date": event_date_formatted,
                    "event_location": event_location,
                    "addit_info": additional_info,
                    "event_manager": event_manager,
                    "event_status": "pending",
                    "submission_date": today,
                    "form_id": form_id
                }
            }
            hs = HandShake("HandshakeDB")
            result = hs.updateStudentForm(data)
            student_info = hs.getStudentName(user_id)[0]
            if result:
                body = render_template('emails/notificationAdmin.html', event_name=event_name, event_role=event_role, event_date=event_date, full_name = student_info[0] + " " + student_info[1])
                msg = Message(subject="Application submitted notification", sender='re-link-noreply@msmary.re-link.edu', recipients=["admin@test.com"], html=body)
                mail.send(msg)
                return redirect(url_for("status"))
            else:
                return render_template('editForm.html', error= "Sorry, there was an error updating your form. Try again later please.")
        else:
            return render_template('editForm.html', error='Please ensure all required fields filled out properly.')

@app.route('/updateFormStatus', methods=['POST'])
def updateFormStatus():
    user_id = session.get('user_id')
    admin_id = session.get('admin_id')
    if user_id is not None:
        return redirect(url_for('index'))
    if admin_id is None:
        return redirect(url_for('adminlogin'))
    if request.method == "POST":
        form_id = request.form['form_id']
        status = request.form['pending_status']
        event_type = request.form['event_type']
        hs = HandShake("HandshakeDB")
        data = (status, form_id)
        result = hs.updateFormStatus(data)
        if result:
            email_info = hs.getEvaluationEmailInfo(form_id)[0]
            if email_info:
                student_name = email_info[0] + " " + email_info[1]
                body = render_template('emails/email.html', full_name = student_name, event_name=email_info[2], event_role=email_info[3], event_date=email_info[4], event_location=email_info[5], event_status=email_info[6])
                msg = Message(subject="Application Evaluated!", sender='re-link-noreply@msmary.re-link.edu', recipients=[email_info[7]], html=body)
                mail.send(msg)

            if event_type == "management":
                flash(f"Succesfully updated the form!")
                return redirect(url_for('management'))
            if event_type == "participation":
                flash(f"Succesfully updated the form!")
                return redirect(url_for('participation'))
        else:
            if event_type == "management":
                flash("Sorry, there was an error saving the evaluation, try again later please.")
                return redirect(url_for('management'))
            if event_type == "participation":
                flash("Sorry, there was an error saving the evaluation, try again later please.")
                return redirect(url_for('participation'))
    else:
        return redirect(url_for('adminlogin'))
    
@app.route('/deleteFormAdmin', methods=['POST'])
def deleteFormAdmin():
    if request.method == 'POST':
        form_id = request.form['form_id']
        event_type = request.form['event_type']
        admin_id = session.get('admin_id')
        if not admin_id:
            return redirect(url_for('adminlogin'))
        hs = HandShake("HandShakeDB")
        result = hs.deleteForm(form_id)
        if result:
            if event_type == "management":
                flash(f"Succesfully deleted the form!")
                return redirect(url_for('management'))
            if event_type == "participation":
                flash(f"Succesfully deleted the form!")
                return redirect(url_for('participation'))
        else:
            if event_type == "management":
                flash("Sorry, there was an error deleting the form, try again later please.")
                return redirect(url_for('management'))
            if event_type == "participation":
                flash("Sorry, there was an error deleting the form, try again later please.")
                return redirect(url_for('participation'))
    else:
        return redirect(url_for('adminlogin'))

@app.route('/deleteForm', methods=['POST'])
def deleteForm():
    if request.method == 'POST':
        form_id = request.form['form_id']
        user_id = session.get('user_id')
        if not user_id:
            return redirect(url_for('login'))
        hs = HandShake("HandShakeDB")
        forms = hs.getStudentForms(user_id)
        valid = False
        for form in forms:
            if form[0] == int(form_id):
                valid = True
        if valid:
            result = hs.deleteForm(form_id)
            if result:
                return redirect(url_for('status'))
            else:
                flash('There was an error deleting your form. Try again later.')
                return redirect(url_for('status'))
        else:
            flash('There was an error deleting your form. Try again later.')
            return redirect(url_for('status'))

@app.route('/status', methods=['GET'])
def status():
    user_id = session.get('user_id')
    if user_id is not None:
        hs = HandShake("HandshakeDB")
        forms = hs.getStudentForms(user_id)
        return render_template('status.html', forms = forms)
    else:
        return redirect(url_for('login'))

def validate_form(event_name, event_location, additional_info):
    if event_name and event_location:
        if len(additional_info) < 300:
            return True
        
    return False

# When form is created, send an email to admin
@app.route('/forms', methods=['GET', 'POST'])
def forms():
    user_id = session.get('user_id')
    if request.method == 'GET':
        if user_id is not None:
            return render_template('forms.html')
        else:
            return redirect(url_for('login'))
    if request.method == 'POST':
        if user_id is not None:
            try:
                event_role = request.form.get('role').split('_')[1].lower()
                event_name = request.form.get('name')
                event_manager = request.form.get('manager')
                event_location = request.form.get('location')
                additional_info = request.form.get('additional_info')
                event_date_str = request.form.get('date')
                event_date = datetime.strptime(event_date_str, '%Y-%m-%d').date()
                event_date_formatted = event_date.strftime('%Y-%m-%d')
                today = date.today()
                if validate_form(event_name, event_location, additional_info):
                    if not additional_info:
                        additional_info = None
                    if not event_manager:
                        event_manager = None
                    data = {
                        "forms":{
                            "event_role": event_role,
                            "event_name": event_name,
                            "event_date": event_date_formatted,
                            "event_location": event_location,
                            "addit_info": additional_info,
                            "event_manager": event_manager,
                            "event_status": "pending",
                            "student_id": user_id,
                            "submission_date": today
                        }
                    }
                    hs = HandShake("HandshakeDB")
                    result = hs.insertForm(data)
                    if result:
                        student_info = hs.getStudentName(user_id)[0]
                        student_email = hs.getStudentEmail(user_id)[0]
                        body = render_template('emails/notificationAdmin.html', event_name=event_name, event_role=event_role, event_date=event_date, full_name = student_info[0] + " " + student_info[1])
                        msg = Message(subject="Application submitted notification", sender='re-link-noreply@msmary.re-link.edu', recipients=["admin@test.com"], html=body)
                        mail.send(msg)
                        body_student = render_template('emails/notificationUser.html', full_name = student_info[0] + " " + student_info[1], event_name=event_name, event_role=event_role, event_date=event_date)
                        msg_student = Message(subject="Application submitted notification", sender='re-link-noreply@msmary.re-link.edu', recipients=[student_email[0]], html=body_student)
                        mail.send(msg_student)
                        success = f"Your event {event_role} form for '{event_name}' has been successfully submitted. It is now pending approval. You will be notificed once it has been approved."
                        return render_template('forms.html', success=success)
                    else:
                        error = "Sorry, an error has occured processing your form. Please try again later."
                        return render_template('forms.html', error = error)
                else:
                    error = "Please ensure the required fields are filled in properly."
                    return render_template('forms.html', error = error)
            except Exception as e:
                error = "Please ensure the required fields are filled in properly."
                return render_template('forms.html', error = error)
        else:
            return redirect(url_for('login'))

@app.route('/logout', methods=['GET'])
def logout():
    user_id = session.get('user_id')
    admin_id = session.get('admin_id')
    if user_id is not None or admin_id is not None:
        session.clear()
        return redirect(url_for('login'))
    else:
        return redirect(url_for('login'))


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    user_id = session.get('user_id')
    if user_id is not None:
        return render_template('index.html')
    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['password_confirm']
        error = validate_sign_up(first_name, last_name, email, password, confirm_password)
        if error:
            return redirect(url_for('index'))
        else:
            try:
                hashed_password = sha256(password.encode()).hexdigest()
                user_name = last_name + first_name
                data = {
                    "student":{
                        "first_name": first_name.capitalize().strip(),
                        "last_name": last_name.capitalize().strip(),
                        "email": email,
                        "password": hashed_password,
                        "user_name": user_name 
                    }
                }
                hs = HandShake("HandshakeDB")
                result = hs.db.getEmailFromStudents(data)
                if not result:
                    code = secrets.token_hex(32)
                    session['register_code'] = code
                    session['user'] = data
                    link = f"http://127.0.0.1:5000/verify?email={urllib.parse.quote(email)}&code={urllib.parse.quote(code)}"
                    body = f"<h1>Hello {first_name},</h1>"\
                                "<p>You've registered for re-link. Please click the verify link below to verify your account.</p>"\
                                f"<a href ='{link}'> Verify! </a>"
                    msg = Message(subject='Registration Verification', sender='re-link-noreply@msmary.re-link.edu', recipients=[email], html=body)
                    mail.send(msg)
                    success = "An email has been sent to your Mount email. Please click the link in the email to verify this is you."
                    return render_template('signup.html', success=success)
                else:
                    error = "This student already exits in the system."
                    return render_template('signup.html', error=error)
                
            except Exception as e:
                error = "An error has occured on our side. Please try again later!"
                return render_template('signup.html', error=error)

    else:
        return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    user_id = session.get('user_id')
    error = "Email or Password entered is incorrect."
    if user_id is not None:
        return redirect(url_for('index'))

    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        if email and password:
            try:
                hashed_password = sha256(password.encode()).hexdigest()
                data = {
                    "student": {
                        "email": email,
                        "password":hashed_password
                    }
                }
                db = HandShake("HandshakeDB")
                result = db.getStudentInfo(data)
                if result:
                    student = result[0]
                    session['user_id'] = student[0]
                    session['username'] = student[1]
                    return redirect(url_for('index'))
                else:
                    return render_template('login.html', error=error)
            except Exception as e:
                return render_template('login.html', error='Sorry, there is a problem on our end. Try again later.')
        else:     
            return render_template('login.html', error=error)
    else:
        return render_template('login.html')

@app.route('/participation', methods=['GET', 'POST'])
def participation():
    user_id = session.get('user_id')
    admin_id = session.get('admin_id')
    if user_id is not None:
        return redirect(url_for('index'))
    if admin_id is None:
        return redirect(url_for('adminlogin'))
    if request.method == 'GET':
        hs = HandShake("HandshakeDB")
        forms = hs.getParticipationForms()
        if forms:
            return render_template('participation.html', forms = forms)
        else:
            flash('Sorry, there are no event participation forms submitted at this time.')
            return render_template('participation.html')
    else:
        return render_template('participation.html')

@app.route('/management', methods=['GET', 'POST'])
def management():
    user_id = session.get('user_id')
    admin_id = session.get('admin_id')
    if user_id is not None:
        return redirect(url_for('index'))
    if admin_id is None:
        return redirect(url_for('adminlogin'))
    if request.method == 'GET':
        hs = HandShake("HandshakeDB")
        forms = hs.getManagementForms()
        if forms:
            return render_template('management.html', forms = forms)
        else:
            flash('Sorry, there are no event management forms submitted at this time.')
            return render_template('management.html')
    else:
        return render_template('management.html')



@app.route('/adminlogin', methods=['GET','POST'])
def adminlogin():
    user_id = session.get('user_id')
    admin_id = session.get('admin_id')
    error = "Email or Password entered is incorrect."
    if user_id is not None:
        return redirect(url_for('index'))
    if admin_id is not None:
        return redirect(url_for('management'))
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        if email and password:
            try:
                hashed_password = sha256(password.encode()).hexdigest()
                data = {
                    "admin":{
                        "email":email,
                        "password":hashed_password
                    }
                }
                db = HandShake("HandshakeDB")
                result = db.getAdminLogin(data)
                if result:
                    admin_id = result[0]
                    session['admin_id'] = admin_id
                    session['username'] = result[1] + result[2]
                    return redirect(url_for('management'))
                else:
                    return render_template('adminlogin.html', error=error)
            except Exception as e:
                return render_template('adminlogin.html', error=error)
            
        else:
            return render_template('adminlogin.html', error=error)
    else:
        return render_template('adminlogin.html')

if __name__ == '__main__':
    app.run(debug=True)