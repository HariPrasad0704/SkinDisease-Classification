import ibm_db

conn = ibm_db.connect("DATABASE=bludb;HOSTNAME=b1bc1829-6f45-4cd4-bef4-10cf081900bf.c1ogj3sd0tgtu0lqde00.databases.appdomain.cloud;PORT=32304;PROTOCOL=TCPIP;UID=jxc07622;PWD=f2QKpEo3wHhq0qGV;Security=SSL;SSLSecurityCertificate=DigiCertGlobalRootCA.crt", "", "")


# conn = ibm_db.connect("DATABASE=bludb;HOSTNAME=b1bc1829-6f45-4cd4-bef4-10cf081900bf.c1ogj3sd0tgtu0lqde00.databases.appdomain.cloud;PORT=32304;PROTOCOL=TCPIP;UID=jxc07622;PWD=f2QKpEo3wHhq0qGV;Security=SSL;SSLSecurityCertificate=DigiCertGlobalRootCA.crt", "", "")
print("Connected to the database")
# except:
#     print("Error in connecting to the database: ", ibm_db.conn_errormsg())


def register(name, email,number, password):
    insert_sql = "INSERT INTO  JXC07622.USER VALUES (?, ?, ?, ?)"
    prep_stmt = ibm_db.prepare(conn, insert_sql)
    ibm_db.bind_param(prep_stmt, 1, name)
    ibm_db.bind_param(prep_stmt, 2, email)
    ibm_db.bind_param(prep_stmt, 3, number)
    ibm_db.bind_param(prep_stmt, 4, password)
    ibm_db.execute(prep_stmt)


def login(name, password):
    select_sql = "SELECT * FROM  JXC07622.USER WHERE USERNAME = ? AND PASSWORD = ?"
    prep_stmt = ibm_db.prepare(conn, select_sql)
    ibm_db.bind_param(prep_stmt, 1, name)
    ibm_db.bind_param(prep_stmt, 2, password)
    out = ibm_db.execute(prep_stmt)
    result_dict = ibm_db.fetch_assoc(prep_stmt)
    print(result_dict)
    return result_dict

def contactInfo(fName,lName,email,number,msg):
    insert_sql = "INSERT INTO JXC07622.CONTACTINFO VALUES (?, ?, ?, ?, ?)"
    prep_stmt = ibm_db.prepare(conn,insert_sql)
    ibm_db.bind_param(prep_stmt, 1, fName)
    ibm_db.bind_param(prep_stmt, 2, lName)
    ibm_db.bind_param(prep_stmt, 3, email)
    ibm_db.bind_param(prep_stmt, 4, number)
    ibm_db.bind_param(prep_stmt, 5, msg)
    ibm_db.execute(prep_stmt)
    
