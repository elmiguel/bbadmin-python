from datetime import datetime
from flask.ext.login import UserMixin
from BbAdminApp import db
import bcrypt


class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    pid = db.Column(db.Integer, unique=True)
    username = db.Column(db.Integer, unique=True)
    firstname = db.Column(db.String(100))
    lastname = db.Column(db.String(100))
    email = db.Column(db.String(200))
    password = db.Column(db.String(255))
    login_method = db.Column(db.String(6), default='LDAP')
    pk1 = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.utcnow())
    modified_at = db.Column(db.DateTime, default=datetime.utcnow())

    def __repr__(self):
        return '<User %r>' % self.username


class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    role_name = db.Column(db.String(50))
    role_type = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow())
    modified_at = db.Column(db.DateTime, default=datetime.utcnow())


def get_or_create(session, model, **kwargs):
    instance = session.query(model).filter_by(**kwargs).first()
    if instance:
        return instance
    else:
        instance = model(**kwargs)
        session.add(instance)
        session.commit()
        return instance

db.create_all()
db.session.commit()

# create test admin user
test = get_or_create(db.session, User,
                     pid=00000, username='BbAdmin', firstname='Admin',
                     lastname='Admin', email='noreply@irsc.edu',
                     login_method='SYSTEM', password=bcrypt.hashpw(b'<SOME_PASSWORD_HERE>', bcrypt.gensalt()),
                     pk1=0
                     )
