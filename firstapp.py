from flask import Flask,render_template,url_for,flash,redirect
from forms import RegistrationForm, LoginForm
from sqlalchemy import create_engine
from flask_bcrypt import Bcrypt
import cx_Oracle
from wtforms.validators import ValidationError

app = Flask(__name__)

app.config['SECRET_KEY'] = '2e3d9442882549964af284ca7d59f157'

engine = create_engine('oracle://dhairya:dhai7735@localhost/orcl')

bcrypt = Bcrypt(app)

@app.route("/")
def home():
    return render_template('home.html')

@app.route("/about")
def about():
    return render_template('about.html')

@app.route("/register", methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        firstname = form.firstname.data
        lastname = form.lastname.data
        email = form.email.data
        password = form.password.data
        hashed_pw = bcrypt.generate_password_hash(password).decode('utf-8')
        # def validate_email(self,email):
        #     email = email.data
        #     result = engine.execute('select * from UserInfo where email = :email',{'email':email})
        #     for row in result:
        #         raise ValidationError('That email is already taken. Please choose another email!')
        # if user:
        #     raise ValidationError('That email is already taken. Please choose another email!')
        engine.execute("insert into UserInfo(FirstName, LastName, email,password) values (:firstname,:lastname,:email,:hashed_pw)",{'firstname':form.firstname.data,'lastname':form.lastname.data,
                        'email':form.email.data,'hashed_pw':hashed_pw})
        # engine.commit()
        # engine.session.commit()
        flash(f'Account created for {form.firstname.data}!', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route("/login", methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit() :
        password_entered = form.password.data
        email_entered = form.email.data
        password_reg = engine.execute("select password from UserInfo where email = :email_entered",{'email_entered':email_entered})
        for row in password_reg:
            reg = row
        if bcrypt.check_password_hash(reg[0] , form.password.data) :
            flash('You have been logged in!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check username and password', 'danger')
    return render_template('login.html', title='Login', form=form)

if __name__ == '__main__':
    app.run(debug=True)