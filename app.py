import os
import uuid
import flask
import urllib
from PIL import Image
from numpy import number
from tensorflow.python.keras.models import load_model
from flask import Flask , render_template  , request , send_file,redirect,url_for,session
from tensorflow.keras.preprocessing.image import load_img , img_to_array
from keras.applications.mobilenet import preprocess_input, decode_predictions
from keras.models import model_from_json
from keras.models import load_model
from mydb import connection as db
import ibm_db,ibm_db_dbi

app = Flask(__name__)
j_file = open('model.json', 'r')
loaded_json_model = j_file.read()
j_file.close()
model = model_from_json(loaded_json_model)
model.load_weights('model.h5')


ALLOWED_EXT = set(['jpg' , 'jpeg' , 'png' , 'jfif'])
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXT

classes = [
   'Actine Keratoses',
   'Basal Cell Carcinoma',
   'Benign Keratosis',
   'Erythema Psoriasis',
   'Melanoma',
   'Melanocytic Nevi',
   'vascular Naevus'

]

conn = ibm_db.connect("DATABASE=bludb;HOSTNAME=b1bc1829-6f45-4cd4-bef4-10cf081900bf.c1ogj3sd0tgtu0lqde00.databases.appdomain.cloud;PORT=32304;PROTOCOL=TCPIP;UID=jxc07622;PWD=f2QKpEo3wHhq0qGV;Security=SSL;SSLSecurityCertificate=DigiCertGlobalRootCA.crt", "", "")
connection = ibm_db_dbi.Connection(conn)
cursor = connection.cursor()

cursor.execute('''CREATE TABLE IF NOT EXISTS user (
	username VARCHAR(50) NOT NULL,  
	gmail VARCHAR(50) NOT NULL, 
    number VARCHAR(50) NOT NULL,
    password VARCHAR(50) NOT NULL
    )''')

cursor.execute('''CREATE TABLE IF NOT EXISTS contactInfo (
	firstName VARCHAR(50) NOT NULL,  
	lastName VARCHAR(50) NOT NULL, 
    email VARCHAR(50) NOT NULL,
    number VARCHAR(50) NOT NULL,
    message VARCHAR(250) NOT NULL
    )''') 

def predict(filename , model):
    img = load_img(filename , target_size = (224, 224))
    img = img_to_array(img)
    img = img.reshape(1,224,224,3)

    img = img.astype('float32')
    img = img/255.0
    result = model.predict(img)

    dict_result = {}
    for i in range(7):
        dict_result[result[0][i]] = classes[i]

    res = result[0]
    res.sort()
    res = res[::-1]
    prob = res[:3]
    
    prob_result = []
    class_result = []
    for i in range(3):
        prob_result.append((prob[i]*100).round(2))
        class_result.append(dict_result[prob[i]])

    return class_result , prob_result

@app.route('/',methods = ['GET','POST'])
def log():
    return render_template('login.html')


@app.route('/login', methods =['GET', 'POST'])
def login():
    msg = ''
    if request.method == 'POST':
        name = request.form["username"]
        password = request.form["password"]
        result_dict = db.login(name,password)
        msg = 'Invalid Username / Password'
        if result_dict != False:
            # session["name"] = request.form["username"]
            # msg = session["name"]
            # print(msg)
            return redirect('/index')
        return render_template('login.html', msg = msg)

    else:
        return render_template('login.html', msg = msg)

@app.route("/register",methods=['GET', 'POST'])
def register():
    msg = ''
    if request.method == 'POST':
        name = request.form["username"]
        email = request.form["email"]
        number = request.form["number"]
        password = request.form["password"]
        print(name,email,password)
        db.register(name,email,number,password)
        return render_template('login.html', msg = msg) 
    else:
        return render_template('register.html', msg = msg)


@app.route('/index')
def home():
        return render_template("index.html")


@app.route('/about/')
def about():
    return render_template("about.html")

@app.route('/contact/')
def contact():
    return render_template("contact.html")

@app.route('/contactInfo',methods=['GET', 'POST'])
def contactInfo():
    if request.method == 'POST':
        fName = request.form["firstName"]
        lName = request.form["lastName"]
        email = request.form["email"]
        number = request.form["number"]
        msg = request.form["msg"]
        print(fName,lName,email,number,msg)
        db.contactInfo(fName,lName,email,number,msg)
        msg1 = 'Success'
        return render_template('contact.html', msg = msg1) 
    else:
        msg2 = 'Please Enter Required Data'
        return render_template('contact.html', msg = msg2)





    


@app.route('/success' , methods = ['GET' , 'POST'])
def success():
    error = ''
    target_img = os.path.join(os.getcwd() , 'static/images')
    if request.method == 'POST':
        if(request.form):
            link = request.form.get('link')
            try :
                resource = urllib.request.urlopen(link)
                unique_filename = str(uuid.uuid4())
                filename = unique_filename+".jpg"
                img_path = os.path.join(target_img , filename)
                output = open(img_path , "wb")
                output.write(resource.read())
                output.close()
                img = filename

                class_result , prob_result = predict(img_path , model)

                predictions = {
                      "class1":class_result[0],
                        "class2":class_result[1],
                        "class3":class_result[2],
                        "prob1": prob_result[0],
                        "prob2": prob_result[1],
                        "prob3": prob_result[2],
                }

            except Exception as e : 
                print(str(e))
                error = 'This image from this site is not accesible or inappropriate input'

            if(len(error) == 0):
                return  render_template('success.html' , img  = img , predictions = predictions)
            else:
                return render_template('index.html' , error = error) 

            
        elif (request.files):
            file = request.files['file']
            if file and allowed_file(file.filename):
                file.save(os.path.join(target_img , file.filename))
                img_path = os.path.join(target_img , file.filename)
                img = file.filename

                class_result , prob_result = predict(img_path , model)

                predictions = {
                      "class1":class_result[0],
                        "class2":class_result[1],
                        "class3":class_result[2],
                        "prob1": prob_result[0],
                        "prob2": prob_result[1],
                        "prob3": prob_result[2],
                }

            else:
                error = "Please upload images of jpg , jpeg and png extension only"

            if(len(error) == 0):
                return  render_template('success.html' , img  = img , predictions = predictions)
            else:
                return render_template('index.html' , error = error)

    else:
        return render_template('index.html')



if __name__ == "__main__":
    app.run(debug = True)   
