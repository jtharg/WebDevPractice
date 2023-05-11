from DB import DB
from mysql.connector import Error

class HandShake():
    def __init__(self, DB_NAME):
        self.DB_NAME = DB_NAME
        self.db = DB(DB_NAME)
        if self.db.currentDB() is None:
            self.create()
            self.db = DB(DB_NAME)

    def create(self):
        self.db.createDatabase(self.DB_NAME)
        self.Tables = {}
        self.defineStudents()
        self.defineForms()
        self.defineAdmin()
        self.db.createTables(self.Tables)

    def defineStudents(self):
        self.Tables["students"] = "CREATE TABLE IF NOT EXISTS {}.`students` ("\
            "`id` INT UNSIGNED NOT NULL AUTO_INCREMENT,"\
            "`first_name` NVARCHAR(200) NOT NULL,"\
            "`last_name` NVARCHAR(200) NOT NULL,"\
            "`email` NVARCHAR(200) NOT NULL,"\
            "`password` VARCHAR(45) NOT NULL,"\
            "`user_name` NVARCHAR(100) NOT NULL,"\
            "PRIMARY KEY (`id`),"\
            "UNIQUE INDEX `email_UNIQUE` (`email` ASC) VISIBLE,"\
            "UNIQUE INDEX `user_name_UNIQUE` (`user_name` ASC) VISIBLE)"\
            "ENGINE = InnoDB;".format(self.DB_NAME)
    
    def defineForms(self):
        self.Tables["forms"] = "CREATE TABLE IF NOT EXISTS {}.`HandshakeDB`.`forms` ("\
            "`form_id` INT UNSIGNED NOT NULL AUTO_INCREMENT,"\
            "`event_role` ENUM('management', 'participation') NOT NULL,"\
            "`event_name` VARCHAR(150) NOT NULL,"\
            "`event_date` DATE NOT NULL,"\
            "`event_location` VARCHAR(300) NOT NULL,"\
            "`addit_info` VARCHAR(300) NULL,"\
            "`event_manager` VARCHAR(200) NULL,"\
            "`event_status` ENUM('pending', 'accepted', 'rejected', 'redraft') NOT NULL,"\
            "`student_id` INT UNSIGNED NOT NULL,"\
            "`submission_date` DATE NOT NULL,"\
            "PRIMARY KEY (`form_id`),"\
            "INDEX `fk_student_form_id_idx` (`student_id` ASC) VISIBLE,"\
            "CONSTRAINT `fk_student_form_id`"\
                "FOREIGN KEY (`student_id`)"\
                "REFERENCES `HandshakeDB`.`students` (`id`)"\
                "ON DELETE NO ACTION"\
                "ON UPDATE NO ACTION)"\
            "ENGINE = InnoDB;".format(self.DB_NAME)
        
    def defineAdmin(self):
        self.Tables["admin"] = "CREATE TABLE IF NOT EXISTS {}.`admin` ("\
        "`admin_id` INT UNSIGNED NOT NULL AUTO_INCREMENT,"\
        "`first_name` VARCHAR(150) NOT NULL,"\
        "`last_name` VARCHAR(150) NOT NULL,"\
        "`password` VARCHAR(300) NOT NULL,"\
        "`email` VARCHAR(150) NOT NULL,"\
        "PRIMARY KEY (`admin_id`))"\
        "ENGINE = InnoDB;".format(self.DB_NAME)
    
    def deleteForm(self, form_id):
        try:
            self.Delete = f'DELETE FROM forms WHERE form_id = {form_id};'
            self.db.delete(self.Delete)
            return True
        except Exception as e:
            return False

    def insertStudent(self, data):
        try:
            self.Insert = {}
            email = self.db.getEmailFromStudents(data)
            if email:
                return False
            else:
                columns = data["student"].keys()
                cols_comma_separated = ', '.join(columns)
                binds_comma_separated = ', '.join(['%(' + item + ')s' for item in columns])
                sql = f'INSERT INTO students ({cols_comma_separated}) VALUES ({binds_comma_separated})'
                self.Insert["student"] = sql
                self.db.insertValues(self.Insert["student"], data["student"])
                return True 
        except Error as e:
            return False
        
    def updateStudentForm(self, data):
        try:
            self.Update = {}
            sql = "UPDATE forms SET event_role = %(event_role)s, event_name = %(event_name)s, event_date = %(event_date)s, event_location = %(event_location)s, addit_info = %(addit_info)s, event_manager = %(event_manager)s, event_status = %(event_status)s, submission_date = %(submission_date)s WHERE form_id = %(form_id)s;"
            self.Update["forms"] = sql
            self.db.update(self.Update["forms"], data["forms"])
            return True
        except Exception as e:
            return False
    
    def getManagementForms(self):
        try:
            self.Select = {}
            sql = "SELECT f.*, s.first_name, s.last_name, s.email FROM forms f INNER JOIN students s ON f.student_id = s.id WHERE event_role = 'management' ORDER BY submission_date DESC, CASE event_status WHEN 'pending' THEN 1 WHEN 'redraft' THEN 2 WHEN 'accepted' THEN 3 WHEN 'rejected' THEN 4 ELSE 5 END;"
            self.Select = sql
            result = self.db.selectRecords(self.Select)
            if result:
                return result
            else:
                return None
        except Exception as e:
            return None
        
    def getParticipationForms(self):
        try:
            self.Select = {}
            sql = "SELECT f.*, s.first_name, s.last_name, s.email FROM forms f INNER JOIN students s ON f.student_id = s.id WHERE event_role = 'participation' ORDER BY submission_date DESC, CASE event_status WHEN 'pending' THEN 1 WHEN 'redraft' THEN 2 WHEN 'accepted' THEN 3 WHEN 'rejected' THEN 4 ELSE 5 END;"
            self.Select = sql
            result = self.db.selectRecords(self.Select)
            if result:
                return result
            else:
                return None
        except Exception as e:
            return None


    def updateFormStatus(self, data):
        try:
            self.Update = {}
            sql = "UPDATE forms SET event_status = %s WHERE form_id = %s;"
            self.Update["forms"] = sql
            self.db.update(self.Update["forms"], data)
            return True
        except Exception as e:
            return False

    def getAdminLogin(self, data):
        try:
            self.Select = {}
            sql = "SELECT admin_id, first_name, last_name, password, email FROM admin WHERE email = %s AND password = %s;"
            self.Select["admin"] = sql
            result = self.db.selectAdminLogin(self.Select["admin"], (data["admin"]['email'], data['admin']['password']))
            if result:
                return result
            else:
                return None
        except Exception as e:
            return None
        

    def getStudentForms(self, user_id):
        try:
            self.Select = f'SELECT * FROM forms WHERE student_id = {user_id};'
            return self.db.selectRecords(self.Select)
        except Exception as e:
            return False
        
    def getEvaluationEmailInfo(self, form_id):
        self.Select = f'SELECT s.first_name, s.last_name, f.event_name, f.event_role, f.event_date, f.event_location, f.event_status, s.email FROM students s INNER JOIN forms f on f.student_id = s.id WHERE form_id = {form_id};'
        try:
            result = self.db.selectRecords(self.Select)
            if result:
                return result
            else:
                return None
        except Exception as e:
            return None
        
    def insertForm(self, data):
        try:
            self.Insert = {}
            columns = data["forms"].keys()
            cols_comma_separated = ', '.join(columns)
            binds_comma_separated = ', '.join(['%(' + item + ')s' for item in columns])
            sql = f'INSERT INTO forms ({cols_comma_separated}) VALUES ({binds_comma_separated})'
            self.Insert["forms"] = sql
            self.db.insertValues(self.Insert["forms"], data["forms"])
            return True
        except Error as e:
            return False

    def getStudentEmail(self, user_id):
        self.Select = f"SELECT email FROM students WHERE id = '{user_id}';"
        return self.db.selectRecords(self.Select)

    def getStudentInfo(self, data):
        self.Select = f"SELECT id, user_name, email, password FROM students WHERE '{data['student']['email']}' = email AND '{data['student']['password']}' = password;"
        return self.db.selectRecords(self.Select)

    def getStudentName(self, user_id):
        self.Select = f"SELECT first_name, last_name FROM students WHERE id = '{user_id}';"
        return self.db.selectRecords(self.Select)
               
    def status(self):
        result = self.db.serverInfo()
        if result is not None:
            self.db.showTables()
        return result
    
    def close(self):
        self.db.closeDatabase()

    