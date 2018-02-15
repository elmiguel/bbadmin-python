from flask.ext.login import UserMixin
from sqlalchemy import *
from sqlalchemy.orm import sessionmaker, relationship, relation
from sqlalchemy.ext.declarative import as_declarative
from bba_config import BBA_OPENDB_URL, DATE, DATETIME, BBA_SCHEMA, BBA_OPENDB_SYSTEM_ROLES
import json
import datetime
from BbAdminApp import db


@as_declarative()
class BBase(object):
    def __tablename__(cls):
        return cls.__name__.lower()

    __table_args__ = {'schema': BBA_SCHEMA, 'autoload': True}
    pk1 = Column(Integer, primary_key=True)

    def as_dict(self):
        return {
            k: v.strftime(DATETIME) if isinstance(v, datetime.datetime)
            else v.strftime(DATE) if isinstance(v, datetime.date)
            else v
            for k, v in {c.name: getattr(self, c.name) for c in self.__table__.columns}.items()
        }

    def to_json(self):
        return json.dumps(self.as_dict())

# When in doubt......debug it!
# This will trace out the entire session
debug = False

# Create and engine and get the metadata
Base = BBase()
engine = create_engine(BBA_OPENDB_URL, echo=debug)

# Bind the engine directly to the Base
Base.metadata.bind = engine


class CourseMain(BBase):
    __tablename__ = 'COURSE_MAIN'
    enrollments = relationship('CourseUsers', back_populates='course')


class CourseUsers(BBase):
    __tablename__ = 'COURSE_USERS'
    users_pk1 = Column(Integer, ForeignKey('BBLEARN.USERS.pk1'))
    crsmain_pk1 = Column(Integer, ForeignKey('BBLEARN.COURSE_MAIN.pk1'))
    data_src_pk1 = Column(Integer, ForeignKey('BBLEARN.DATA_SRC.pk1'))
    user = relationship('Users', back_populates='enrollments')
    course = relationship('CourseMain', back_populates='enrollments')

    # There is no ForeignKey between CourseUsers and Data_Source Tables, so we make one on the fly ;)
    data_source = relation('DataSource', backref='CourseUsers',
                           primaryjoin='CourseUsers.data_src_pk1==DataSource.pk1',
                           foreign_keys='DataSource.pk1')


class DataSource(BBase):
    __tablename__ = 'DATA_SOURCE'
    # course_dsk = relationship('CourseUsers', back_populates='data_source')


class Users(BBase):
    __tablename__ = 'USERS'
    institution_roles_pk1 = Column(Integer, ForeignKey('BBLEARN.INSTITUTION_ROLES.pk1'))
    system_role = Column(String(50))
    enrollments = relationship('CourseUsers', back_populates='user')
    user_roles = relation('UserRoles', back_populates='user')


class UserRoles(BBase):
    __tablename__ = 'USER_ROLES'
    users_pk1 = Column(Integer, ForeignKey('BBLEARN.USERS.pk1'))
    institution_roles_pk1 = Column(Integer, ForeignKey('BBLEARN.INSTITUTION_ROLES.pk1'))
    data_src_pk1 = Column(Integer, ForeignKey('BBLEARN.DATA_SRC.pk1'))
    user = relationship('Users', back_populates='user_roles')
    data_source = relation('DataSource', backref='UserRoles',
                           primaryjoin='UserRoles.data_src_pk1==DataSource.pk1',
                           foreign_keys='DataSource.pk1')
    institution_role = relationship('InstitutionRoles', back_populates='user_role')


class InstitutionRoles(BBase):
    __tablename__ = 'INSTITUTION_ROLES'
    data_src_pk1 = Column(Integer, ForeignKey('BBLEARN.DATA_SRC.pk1'))
    user_role = relationship('UserRoles', back_populates='institution_role')


class SystemRoles(BBase):
    __tablename__ = 'SYSTEM_ROLES'

# Create a session to use the tables
Session = sessionmaker(bind=engine)
open_db_session = Session()

# ======================================================================================================================
# Users
# ======================================================================================================================


# Local DB setup, Singular in Term for class name
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
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow())
    modified_at = db.Column(db.DateTime, default=datetime.datetime.utcnow())

    def __repr__(self):
        return '<User %r>' % self.username


class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    role_name = db.Column(db.String(50))
    role_type = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow())
    modified_at = db.Column(db.DateTime, default=datetime.datetime.utcnow())


def get_or_create(session, model, **kwargs):
    instance = session.query(model).filter_by(**kwargs).first()
    if instance:
        # print("Record already exists, returning model.id: %s" % instance.id)
        return instance
    else:
        # print("Attempting to insert new record: [{}]".format(**kwargs))
        instance = model(**kwargs)
        session.add(instance)
        session.commit()
        # print("Insert/Commit complete")
        return instance

# users = open_db_session.query(Users).filter(func.REGEXP_LIKE(Users.batch_uid, '^[[:digit:]]+$')).limit(2).offset(4)
users = open_db_session.query(Users).filter(func.REGEXP_LIKE(Users.batch_uid, '^[[:digit:]]+$')).all()

# for user in users:
#     for enrollment in user.enrollments:
#         for dsk in enrollment.data_source:
#             print("User: {}, Course: {}, DSK: {}".format(user.user_id, enrollment.course.course_id, dsk.batch_uid))

# for user in users:
#     for role in user.user_roles:
#         for dsk in role.data_source:
#             print("User: {}, System Role: {} [{}], Institution Role: {}, DSK: {}".format(
#                 user.user_id, BBA_OPENDB_SYSTEM_ROLES[user.system_role], user.system_role,
#                 role.institution_role.role_name, dsk.batch_uid)
#             )

for user in users:
    print(user)
    local_user = get_or_create(db.session, User,
                               pid=user.batch_uid,
                               username=user.user_id,
                               firstname=user.firstname,
                               lastname=user.lastname,
                               email=user.email,
                               pk1=user.pk1)

    get_or_create(db.session, Role,
                  user_id=local_user.id,
                  role_name=user.system_role,
                  role_type='System Role')

    for role in user.user_roles:
        get_or_create(db.session, Role,
                      user_id=local_user.id,
                      role_name=role.institution_role.role_name,
                      role_type='Institution Role')
print("Open DB Snapshot complete!")
