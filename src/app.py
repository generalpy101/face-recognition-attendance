import datetime
from flask import (
    Flask,
    flash,
    render_template,
    Response,
    request,
    jsonify,
    redirect,
    url_for,
    session,
)
from models import db, Student
import os
from makeRequests import FaceDetection
import base64, json
from flask_login import LoginManager
from flask_login import login_required, logout_user, current_user, login_user
from dotenv import load_dotenv

load_dotenv()

URL = os.getenv("BASE_URL")


login_manager = LoginManager()

basedir = os.path.abspath(os.path.dirname(__file__))

BASE64STR = "data:image/png;base64,"
ROWPERPAGE = 10

f = FaceDetection(URL)
PERSONGROUPID = os.getenv("PERSONGROUP_ID")

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///students.sqlite3"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = "123"


db.init_app(app)
login_manager.init_app(app=app)


@app.route("/")
def index():
    logout_on_start()
        
    return render_template("index.html")

@app.route("/capture") 
def capture() :
    logout_on_start()
    return render_template("capture.html")

@app.route("/identify-face", methods=["GET","POST"])
def detectFace():
    try :
        attendanceAlreadyRecorded = []
        data = request.json
        images = data.get("images")
        images = base64.b64decode(images.replace(BASE64STR, ""))
        personIds = f.IdentifyFace("test1", images, 0.6, 1)
        students = []
        if not(len(personIds) > 0 ) :
            return Response("User not found",status=401)
        today = datetime.datetime.now()
        for i in personIds:
            s = Student.query.filter_by(uuid=i).first()
            # if s.last_attendance.date() == today.date() :
            #     return Response("Already registered attendance",status=409)
            s.attendance = s.attendance + 1
            jsonData = {
                "name": s.name,
                "regid": s.regid,
                "rollno": s.rollno,
                "branch": s.branch,
                "year": s.year,
                "attendance": s.attendance,
            }
            db.session.commit()
            students.append(jsonData)
        return redirect(
            url_for(
                "studentDetails",
                data=base64.b64encode(json.dumps(students).encode("utf-8")),
            ),
            code=307,
        )
    except Exception as e :
        print(e)
        return redirect(url_for("capture"),code=404)


@app.route("/login-student", methods=["GET", "POST"])
def loginStudent():
    logout_on_start()
    if request.method == "POST" :
        data = request.json
        regid = data.get("regid")
        password = data.get("password")
        student = Student.query.filter_by(regid = regid).first()
        if student and student.check_password(password=password) :
            login_user(student)
            session["user_as"] = "student"
            print("logged in")
            return redirect(url_for("studentDashboard"))
        return Response("Invalid ceredentials",status=401 )
    return render_template("student-login.html")

@app.route("/login-admin",methods = ["GET","POST"])
def loginAdmin() :
    logout_on_start()
    if request.method == "POST" :
        data = request.json
        username = data.get("username")
        password = data.get("password")
        if username == "admin" and password == "admin" :
            if session.get("user_as") == "student" : logout()
            session["user_as"] = "admin"
            return redirect(url_for("adminDashboard"))
        else :
            flash("Invalid ceredentials")
            return Response("Invalid credentials",status=401)
    return render_template("admin-login.html")

@app.route("/admin-dashboard")
def adminDashboard() :
    userStatus = session.get("user_as")
    if userStatus != "admin" : 
        flash("Error, you have to be logged in to access that page")
        return redirect(url_for("index"),code = 401)
    page = request.args.get("page",1,type=int)
    students = Student.query.paginate(page=page,per_page =ROWPERPAGE)  
    return render_template("admin-dashboard.html",students=students)

@app.route("/delete",methods=["POST"])
def delete () :
    userStatus = session.get("user_as")
    if userStatus != "admin" : 
        flash("Error, you have to be logged in to access that page")
        return redirect(url_for("index"),code = 401)
    uuid = request.json.get("uuid",None)
    if uuid == None :
        return Response("Bad request no uuid provided",status=400)
    s = Student.query.filter_by(uuid=uuid)
    if not (s is None) :
        api = f.DeletePerson("test1",uuid)
        if not api :
            return Response("Error internal server",500)
        s.delete()
        db.session.commit()
        return redirect(url_for("adminDashboard"))
    else :
        return Response("No such user exists",status=550)

@app.route("/student-dashboard")
@login_required
def studentDashboard() :
    return render_template("student-dashboard.html",today = datetime.datetime.now())

@app.route("/student-details")
def studentDetails():
    logout_on_start()
    jsonB64 = request.args.get("data")
    jsonB64 = json.loads(base64.b64decode(jsonB64))
    print(jsonB64)
    return render_template("student-details.htm", data=jsonB64)


@app.route("/register")
def register_template():
    logout_on_start()
    return render_template("form.html")


@app.route("/register-student", methods=["POST"])
def addData():
    try:
        data = request.json
        images = data.get("images")
        passwd = data.get("password","root")
        name = data.get("name")
        regid = data.get("regid")
        rollno = data.get("rollno")
        branch = data.get("branch")
        year = data.get("year")
        images = base64.b64decode(images.replace(BASE64STR, ""))
        multipleFace = f.DetectPerson("test1",images)
        if (len(multipleFace) > 1) : 
            return Response("Error multiple faces detected",status = 404)
        if (len(multipleFace) <= 0) :
            return Response("Error no face detected",status = 404)
        personIds = f.IdentifyFace("test1", images, 0.6, 1)
        if personIds != None  : 
            if  len(personIds) > 0 : 
                return Response("Error user face is already registered",status=409)
        existing = Student.query.filter_by(regid = regid,rollno=rollno).first()
        if not (existing is None) :
            return Response("User already exists",status=409)
        pid = f.AddPersonToPersonGroup(
            PERSONGROUPID, data.get("name"), data.get("regid"), [images]
        )
        print(pid)
        s = Student(pid, name, regid, rollno, branch, year)
        s.set_password(passwd)
        db.session.add(s)
        db.session.commit()
        # login_user(s)
        flash("User registered successfully")
        return redirect(url_for("index"))
    except Exception as e:
        print(e)
        return Response("Internal server error occured", status=500)

def logout_on_start() :
    if session.get("user_as") != "" :
        session["user_as"] = ""
    
    if current_user.is_authenticated :
        print("Already logged in, logging out")
        return redirect(url_for("logout"))

@app.route("/logout")
@login_required
def logout() :
    print("Logging user out")
    logout_user()
    return redirect(url_for("index"))

@login_manager.user_loader
def load_user(uuid) :
    if uuid is not None :
        return Student.query.get(uuid)
    return None

@login_manager.unauthorized_handler
def unauthorized() :
    flash("You must be logged in to view that page")
    return redirect(url_for("index"))

@app.before_first_request
def initialize_database():
    db.create_all()


if __name__ == "__main__":
    app.run(debug=True)
