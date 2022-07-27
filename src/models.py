from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()


class Student(UserMixin,db.Model):
    def __init__(self,uuid,name,regid,rollno,branch,year):
        self.uuid = uuid
        self.name = name
        self.regid = regid
        self.rollno = rollno
        self.branch = branch
        self.year = year
    
    uuid = db.Column(db.String(255), primary_key=True)
    name = db.Column(db.String(1023), nullable=False)
    regid = db.Column(db.Integer, nullable=False)
    rollno = db.Column(db.Integer, nullable=False)
    password = db.Column(db.String(255),nullable = False)
    branch = db.Column(db.String(255), nullable=False)
    year = db.Column(db.String(255), nullable=False)
    created_on = db.Column(db.DateTime(timezone=True), server_default=func.now())
    last_attendance = db.Column(db.DateTime(timezone=True), server_default=func.now(),onupdate=func.now())
    attendance = db.Column(db.Integer,default=0)
    last_login = db.Column(db.DateTime(timezone=True))

    def __repr__(self) -> str:
        return f"<Student : {self.name}>"
    
    def get_id(self) :
        return self.uuid

    def set_password(self,password) :
        self.password = generate_password_hash(password,method="sha256")
    
    def check_password(self,password) :
        return check_password_hash(self.password,password)