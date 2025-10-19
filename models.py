from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy() 

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, 
                   primary_key=True)

    name = db.Column(db.String(100), 
                     nullable=False)
    
    email = db.Column(db.String(255), 
                      unique=True, 
                      nullable=False, index=True)
    
    hashed_password = db.Column(db.String(255), 
                                nullable=False)

    created_date = db.Column(db.DateTime, 
                             default=datetime.utcnow)
    
    articles = db.relationship('Article', backref='author', lazy=True)
    
    def set_password(self, password):
        self.hashed_password = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.hashed_password, password)
    
    def __repr__(self):
        return f'<User {self.email}>'

class Article(db.Model):
    __tablename__ = 'articles'
    
    id = db.Column(db.Integer, 
                   primary_key=True)

    title = db.Column(db.String(200), 
                      nullable=False)
    
    text = db.Column(db.Text, 
                        nullable=False)
    
    created_date = db.Column(db.DateTime, 
                             default=datetime.utcnow)
    
    user_id = db.Column(db.Integer, 
                        db.ForeignKey('users.id'), 
                        nullable=False)