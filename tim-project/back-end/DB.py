from mysql.connector import connect
from mysql.connector import Error, errorcode

class DB():
    def __init__(self,DB_NAME):
        """ Constructor for myDB
        """
        self.connection = None
        self.checkConfig()
        self.connectDatabase(DB_NAME)

    def cntTables(self):
        """ How many tables for this database
        """
        cursor = self.connection.cursor()
        cursor.execute('SELECT COUNT(*) FROM information_schema.tables ' \
                       'WHERE table_schema="' + self.currentDB() + '"')
        return cursor.fetchone()[0]

    def currentDB(self):
        """ What database is connection using
        """
        if self.connection is not None and self.connection.is_connected():
            cursor = self.connection.cursor()
            cursor.execute("select database();")
            record = cursor.fetchone()[0]
            return record

    def checkConfig(self):
        """ Read configuration file
        user name tagged with user:
        password tagged with password:
        """
        with open("C:\\Users\\harge\WebDevPractice\\tim-project\\back-end\\web_config.txt", "r") as infile:
            data = infile.read()  
        self.config = {}
        for line in data.splitlines():
            vals = line.split(":")
            self.config[vals[0].strip()] = vals[1].strip()
        infile.close()

    def connectDatabase(self,DB_NAME=""):
        """
        Connect MySQL database
        """
        if self.connection is not None and self.connection.is_connected():
            self.connection.close()
        try:
            if len(DB_NAME) > 0:
                self.config["database"] = DB_NAME
            self.connection = connect(**self.config)
        except Error as e:
            if e.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                print("Something is wrong with your user name or password")
            elif e.errno == errorcode.ER_BAD_DB_ERROR:
                print("Database does not exist")
                self.config["database"] = ""
                self.connection = connect(**self.config)
            else:
                print(e)

    def closeDatabase(self):
        """
        Close MySQL connection
        """
        if self.connection is not None and self.connection.is_connected():
            self.connection.close()

    def changeDatabase(self, DB):
        """
        Connect MySQL database
        """
        if self.connection is not None and self.connection.is_connected():
            self.connection.close()
        try:
            self.config["database"] = DB
            self.connection = connect(**self.config)
        except Error as e:
            if e.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                print("Something is wrong with your user name or password")
            elif e.errno == errorcode.ER_BAD_DB_ERROR:
                print("Database does not exist")
            else:
                print(e)

    def serverInfo(self):
        """
        Retrieve and display current connection information
        """
        if self.connection is not None and self.connection.is_connected():
            db_Info = self.connection.get_server_info()
            print("Connected to MySQL Server version ", db_Info)
            cursor = self.connection.cursor()
            cursor.execute("select database();")
            record = cursor.fetchone()[0]
            print("You're connected to database: ", record)
            cursor.close()
            return record

    def showTables(self):
        """
        Display table names for current database
        """
        if self.connection is not None and self.connection.is_connected():
            cursor = self.connection.cursor()
            cursor.execute("SHOW TABLES;")
            values = cursor.fetchall()
            for val in values:
                print(val)
            cursor.close()
    
    def getEmailFromStudents(self, data):
        email = data["student"]["email"]
        cursor = self.connection.cursor()
        try:
            cursor.execute("SELECT id FROM students WHERE email = %s", (email, ))
            result = cursor.fetchone()
            cursor.close()
            if result:
                return result[0]
            else:
                return None
        except Error as e:
            raise Exception("Error in DB.py file.")

    def selectAdminLogin(self, select, data):
        cursor = self.connection.cursor()
        try:
            cursor.execute(select, data)
            result = cursor.fetchone()
            cursor.close()
            if result:
                return result
            else:
                return None
        except Error as e:
            raise Exception("Error in DB.py file.")

    def createDatabase(self,DB_NAME):
        """
        Create database if it does not exist
        """
        cursor = self.connection.cursor()
        try:
            cursor.execute(
                "CREATE DATABASE {} DEFAULT CHARACTER SET 'utf8'".format(DB_NAME))
        except Error as e:
            print("Failed creating database: {}".format(e))

        try:
            cursor.execute("USE {}".format(DB_NAME))
        except Error as e:
            raise Exception("Error in DB.py file.")

    def insertValues(self, insert, data):
        cursor = self.connection.cursor()
        try:
            cursor.execute(insert, data)
            self.connection.commit()
            cursor.close()
        except Error as e:
            raise Exception("Error in DB.py file.")

    def update(self, update, data):
        cursor = self.connection.cursor()
        try:
            cursor.execute(update, data)
            self.connection.commit()
            cursor.close()
        except Error as e:
            raise Exception("Error in DB.py file.")

    def delete(self, delete):
        cursor = self.connection.cursor()
        try:
            cursor.execute(delete)
            self.connection.commit()
            cursor.close()
        except Error as e:
            raise Exception("Error deleting in DB.py file.")


    def selectRecords(self, select):
        cursor = self.connection.cursor()
        try:
            cursor.execute(select)
            records = cursor.fetchall()
            cursor.close()
            return records
        except Error as e:
            raise Exception("Error in DB.py file.")

    def createTables(self,Tables):
        """
        Create tables using dictionary of SQL commands
        """
        cursor = self.connection.cursor()
        for Table in Tables:
            try:
                cursor.execute(Tables[Table])
                print("Creating table {}: \n".format(Table), end='')
            except Error as e:
                if e.errno == errorcode.ER_TABLE_EXISTS_ERROR:
                    print("already exists.")
                else:
                    raise Exception("Error in DB.py file.")
        cursor.close()

            

