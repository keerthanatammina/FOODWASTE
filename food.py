from flask import Flask,flash,render_template,url_for,request,redirect,session,send_from_directory,flash
from requests import get
import random
from otp import genotp
from os.path import join
from flask_mysqldb import MySQL
from datetime import datetime
from py_mail import mail_sender
from email.message import EmailMessage
import smtplib
import os
from itemotp import iotp


app = Flask(__name__)


app.config['MYSQL_HOST'] ='localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD']='lakshmi@2002'
app.config['MYSQL_DB']='food'

mysql=MySQL(app)

app.secret_key=os.urandom(30)

from_mail="sepjune0306@gmail.com"
passcode="eihjpoubvtcpydj"



@app.route('/')
def home():
    return render_template('index.html')

'''
@app.route('/login')
def login():
    return render_template('login.html')'''

'''@app.route('/admin')
def adminlogin():
    return render_template('adminlogin.html')'''

            


@app.route('/signin',methods=["GET","POST"])
def signin():
    error=None
    success=None
    if request.method=="POST":
        fullname=request.form.get('fullname')
        password=request.form.get('password')
        confirmpassword=request.form.get('pass')
        email=request.form.get('email')
        cursor=mysql.connection.cursor()
        cursor.execute('select email from signin')
        emails=cursor.fetchall()
        mysql.connection.commit()
        cursor.close()
        if len(fullname)<4:
            error="YOUR NAME LOOKS INAVLID PLEASE ENTER VALID NAME"
        elif (email,) in emails:
            error="Sorry this Email-Id had used already"
        elif len(email)<6 :
            error="Your email should contain atleast 8 characters without accepting any special symbols only @"
        elif len(password)<6:
            error="Password should have atleast 8 characters and accepts any symbols,characters"
        elif password!=confirmpassword:
            error="Passwords not matched please enter same password"
            
        else:
            otp=genotp()
            subject='Thanks for registering to the application'
            body=f'Use this otp to register {otp}'
            mail_sender(email,subject,body)
            return render_template('otp.html',otp=otp,fullname=fullname,email=email,password=password)
    else:
        flash('Invalid college code')
        return render_template('signin.html') 
    return render_template('signin.html',error=error,msg=success)

@app.route('/otp/<otp>/<fullname>/<password>/<email>',methods=['GET','POST'])
def otp(otp,fullname,password,email):
    if request.method=='POST':
        uotp=request.form['otp']
        if otp==uotp:
            cursor=mysql.connection.cursor()
            lst=[fullname,password,email]
            query='insert into signin \
values(%s,%s,%s)'
            cursor.execute(query,lst)
            mysql.connection.commit()
            cursor.close()
            flash('Details registered')
            
            return redirect(url_for('login'))
        else:
            flash('Wrong otp')
            return render_template('otp.html',otp=otp,fullname=fullname,email=email,password=password)

@app.route("/login",methods=["GET","POST"])
def login():
    error=None
    if request.method=="POST":
        email=request.form.get('email')
        password=request.form.get('password')
        if len(email)<6:
            error="YOUR EMAIL-ID IS INVALID PLEASE ENTER VALID MAIL ADDRESS"
        elif len(password)<6:
            error="PASSWORD IS EMPTY OR INVALID"
        else:
            cursor=mysql.connection.cursor()
            #query="select * from signup where email=%s and password=%s"
            cursor.execute('select * from signin where email=%s and password=%s',[email,password])
            rows=cursor.fetchall()
            countRows=cursor.rowcount
            mysql.connection.commit()
            cursor.close()
            if countRows<1:
                error="INVALID LOGIN DETAILS"
            else:
                session['email']=email
                subject=f'YOUR LOGIN PROCESS DONE SUCCESSFULLY'
                body=f'\nYOUR ACCOUNT HAS BEEN LOGGED IN  SUCCESSFULLY ON ACCOUNT {email}\n\nThanks for being a member in our HUNGRY HARVEST.\n\nHAVE A GREAT MEAL!'
                try:
                    mail_sender(email,subject,body)
                except Exception as e:
                    print(e)
                return redirect(url_for('ingredients'))
                
    return render_template('login.html',error=error)

@app.route("/ingredients")
def ingredients():
    return render_template('ingredients.html')

@app.route("/adminlogin",methods=["GET","POST"])
def adminlogin():
    error=None
    if request.method=="POST":
        email=request.form.get('email')
        password=request.form.get('password')
        if len(email)<6:
            error="YOUR EMAIL-ID IS INVALID PLEASE ENTER VALID MAIL ADDRESS"
        elif len(password)<6:
            error="PASSWORD IS EMPTY OR INVALID"
        else:
            cursor=mysql.connection.cursor()
            #query="select * from signup where email=%s and password=%s"
            cursor.execute('select * from signin where email=%s and password=%s',[email,password])
            rows=cursor.fetchall()
            countRows=cursor.rowcount
            mysql.connection.commit()
            cursor.close()
            if countRows<1:
                error="INVALID LOGIN DETAILS"
            else:
                session['email']=email
                subject=f'YOUR LOGIN PROCESS DONE SUCCESSFULLY'
                body=f'\nYOUR ACCOUNT HAS BEEN LOGGED IN  SUCCESSFULLY ON ACCOUNT {email}\n\nThanks for being a member in our HUNGRY HARVEST.\n\nHAVE A GREAT MEAL!'
                try:
                    mail_sender(email,subject,body)
                except Exception as e:
                    print(e)
                return redirect(url_for('index'))
                
    return render_template('adminlogin.html',error=error)

@app.route("/delivery")
def delivery():
    if request.method=="POST":
        name=request.form.get('name')
        mobile=request.form.get('mobile')
        email=request.form.get('email')
        country=request.form.get('country')
        state=request.form.get('state')
        pincode=request.form.get('pincode')
        address=request.form.get('address')
        cursor=mysql.connection.cursor()
        cursor.execute('insert into delivery(%s,%d,%s,%s,%s,%s,%s)',[name,mobile,
        email,country,state,pincode,address])
        mysql.connection.commit()
        cursor.close()
    return render_template('delivery.html')

@app.route("/adddonations",methods=["GET","POST"])
def adddonations():
    if request.method=="POST":
        Itemname=request.form.get('Itemname')
        quantity=request.form.get('quantity')
        expiredate=request.form.get('expiredate')
        donarname=request.form.get('donarname')
        image=request.files['files']
        filename=image.filename.split('.')[-1]
        if filename!='jpg':
            return 'Pls upload jps images only'
        cursor=mysql.connection.cursor()
        itemid=iotp()
        path=os.path.dirname(os.path.abspath(__file__))
        static_path=os.path.join(path,'static')
        image.save(os.path.join(static_path,f'{itemid}.jpg'))
        cursor.execute('insert into ingredients(itemid,Itemname,quantity,expiredate,donarname) values(%s,%s,%s,%s,%s)',[itemid,Itemname,quantity,expiredate,donarname])
        mysql.connection.commit()
        cursor.close()
        flash("Item added successfully")
    return render_template('adddonations.html')


@app.route("/getfood")
def getfood():
    cursor=mysql.connection.cursor()
    cursor.execute('select ItemId,Itemname,quantity,expiredate from ingredients')
    data=cursor.fetchall()
    #path=os.path.dirname(os.path.abspath(__file__))
    #static_path=os.path.join(path,'static')
    #image.save(os.path.join(static_path,f'{itemid}.jpg'))
    mysql.connection.commit()
    cursor.close()
    return render_template('indepth.html',data=data)


if __name__ == '__main__':
    app.run(debug=True)

