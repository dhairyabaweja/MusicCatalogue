from sqlalchemy import create_engine
import cx_Oracle
password='dhai7735'
host='localhost'
port=1521
sid='orcl'
user='system'

sid = cx_Oracle.makedsn(host,port,sid=sid)

# cstr = 'oracle://{user}:{password}@{sid}'.format(
#     user=user,
#     password=password,
#     sid=sid
# )

# engine =  create_engine(
#     cstr,
#     convert_unicode=False,
#     pool_recycle=10,
#     pool_size=50,
#     echo=True
# )
engine = create_engine('oracle://dhairya:dhai7735@localhost/orcl')

result = engine.execute('select * from new')
for row in result:
    print (row)

