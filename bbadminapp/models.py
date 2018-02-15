# from flask.ext.login import UserMixin
from flask_login import UserMixin
from sqlalchemy.ext.declarative.api import as_declarative
from BbAdminApp import db
from datetime import datetime
import bcrypt


@as_declarative()
class ModelBase(object):
    def __tablename__(self):
        return self.__name__.lower()

    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow())
    modified_at = db.Column(db.DateTime, default=datetime.utcnow())


class User(ModelBase, UserMixin, db.Model):
    __tablename__ = 'users'
    pid = db.Column(db.Integer, unique=True)
    username = db.Column(db.Integer, unique=True)
    firstname = db.Column(db.String(100))
    lastname = db.Column(db.String(100))
    email = db.Column(db.String(200))
    password = db.Column(db.String(255))
    login_method = db.Column(db.String(6), default='LDAP')
    pk1 = db.Column(db.Integer)

    def verify_password(self, password):
        return True if bcrypt.hashpw(bytes(password, encoding='UTF-8'), self.password) == self.password else False

    def __repr__(self):
        return '<User %r>' % self.username


class Role(ModelBase, db.Model):
    __tablename__ = 'roles'


