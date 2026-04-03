from .extensions import db
from flask_login import UserMixin

class Role(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(50), nullable = False)

    def __repr__(self):
        return f"<Role {self.name}>"
    
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    role_id = db.Column(db.Integer, db.ForeignKey("role.id"))
    role = db.relationship("Role")

    def __repr__(self):
        return f"<User {self.email}>"
    
class Record(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float, nullable=False)
    type = db.Column(db.String(10), nullable=False)  
    category = db.Column(db.String(50))
    date = db.Column(db.Date, nullable=False)
    notes = db.Column(db.String(200))
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))