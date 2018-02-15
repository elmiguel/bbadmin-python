#!/usr/local/bin python3.5
import sqlalchemy
import cx_Oracle
from sqlalchemy import create_engine

# user_id=user_id,
# student_id=student_id,
# fullname=firstname + ' ' + lastname,
# first=firstname,
# last=lastname,
# email=email,
# md5='{md5}',
# password=password


debug = True
engine = create_engine(
    'oracle+cx_oracle://<OPENDB_USER>:<OPENDB_PASS>@<OPENDB_IP>:<POR>/<INSTANCE>', echo=debug)
conn = engine.connect()
result = conn.execute("SELECT * FROM BBLEARN.USERS U WHERE U.STUDENT_ID LIKE '(%'")
count = 0

for row in result:
    if count >= 10:
        break
    print(
        row.user_id,
        row.student_id,
        row.firstname + ' ' + row.lastname,
        row.firstname,
        row.lastname,
        row.email,
        row.passwd
    )
    count += 1
conn.close()
