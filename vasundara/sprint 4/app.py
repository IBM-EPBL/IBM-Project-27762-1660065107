from flask import Flask, render_template, request, flash, redirect, url_for, session
import sqlite3
import urllib.request
import os
from werkzeug.utils import secure_filename
import pickle
import numpy as np
from keras.models import load_model
from keras.preprocessing import image


app = Flask(__name__)
app.secret_key="123"
UPLOAD_FOLDER = 'static/uploads/'
dic = {0:'Healthy',1:'Has parkinson'}
train = pickle.load(open('train.pkl','rb'))


app.secret_key = "secret key"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
 
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])
 
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


con=sqlite3.connect("database.db")
con.execute("create table if not exists customer(pid integer primary key,name text,address text,contact integer,mail text)")
con.close()

@app.route('/')
def index():
    return render_template('home.html')

@app.route('/login',methods=["GET","POST"])
def login():
    if request.method=='POST':
        name=request.form['name']
        password=request.form['password']
        con=sqlite3.connect("database.db")
        con.row_factory=sqlite3.Row
        cur=con.cursor()
        cur.execute("select * from customer where name=? and mail=?",(name,password))
        data=cur.fetchone()

        if data:
            session["name"]=data["name"]
            session["mail"]=data["mail"]
            return redirect("customer")
        else:
            flash("Username and Password Mismatch","danger")
    return render_template('login.html')

 
@app.route('/uploads')
def uploads():
    return render_template('index.html')
 
@app.route('/upload_image', methods=['POST'])
def upload_image():
    if 'file' not in request.files:
        flash('No file part')
        return redirect(request.url)
    file = request.files['file']
    if file.filename == '':
        flash('No image selected for uploading')
        return redirect(request.url)
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        #print('upload_image filename: ' + filename)
        flash('Image successfully uploaded and displayed below')
        return render_template('index.html', filename=filename)
    else:
        flash('Allowed image types are - png, jpg, jpeg, gif')
        return redirect(request.url)

    
def predict_label(img):
    i = image.load_img(img_path, target_size=(100,100))
    i = image.img_to_array(i)/255.0
    i = i.reshape(1, 100,100,3)
    p = model.predict_classes(i)
    return dic[p[0]]

@app.route('/predict',methods=['POST'])
def predict():
    file = request.files['file']
    filename = secure_filename(file.filename)
    img_path = "static/uploads"+file.filename
    img.save(img_path)
    flash("Person's status is:" )
    pred = model.predict_label(img_path)
    return render_template('index.html', filename=filename)
    

@app.route('/display/<filename>')
def display_image(filename):
    #print('display_image filename: ' + filename)
    return redirect(url_for('static', filename='uploads/' + filename), code=301)



@app.route('/customer',methods=["GET","POST"])
def customer():
    return render_template("home.html")

@app.route('/register',methods=['GET','POST'])
def register():
    if request.method=='POST':
        try:
            name=request.form['name']
            address=request.form['address']
            contact=request.form['contact']
            mail=request.form['mail']
            con=sqlite3.connect("database.db")
            cur=con.cursor()
            cur.execute("insert into customer(name,address,contact,mail)values(?,?,?,?)",(name,address,contact,mail))
            con.commit()
            flash("Record Added  Successfully","success")
        except:
            flash("Error in Insert Operation","danger")
        finally:
            return redirect(url_for("index"))
            con.close()

    return render_template('register.html')

 
@app.route('/prediction')
def prediction():
    return render_template('prediction.html')
 
@app.route('/about')
def about_us():
    return render_template('aboutus.html')
 

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for("index"))

@app.route("/home/<name>")
def user(name):
    return f"Hello {name}! How are you?"

if __name__ == '__main__':
    app.run()