import mysql.connector
from mysql.connector import Error
import bcrypt
import getpass
from tabulate import tabulate

class DBManager:
    def __init__(self, host, user, password, db_name):
        try:
            self.connection = mysql.connector.connect(
                host=host,
                user=user,
                password=password,
                database=db_name
            )
            if self.connection.is_connected():
                print("Successfully connected to the database.")
        except Error as e:
            print(f"Failed to connect to the database: {e}")
            self.connection = None

    def add_record(self, entity):
        sql_query = None  # Initialize SQL query
        parameters = None  # Initialize parameters
        if entity == "school":
            name = input("Enter School Name: ")
            while True:
                contact = input("Enter phone number (10 digits): ")
                if len(contact) == 10 and contact.isdigit():
                    break  # Valid phone number
                else:
                    print("Error: Phone number must be exactly 10 digits. Please try again.")
            address = input("Enter School's Address: ")
            sql_query = "INSERT INTO school (School_name, School_contact, School_address) VALUES (%s, %s, %s);"
            parameters = (name, contact, address)         
        elif entity == "student":
            Student_name = input("Enter Student's Name: ")
            Student_age = int(input("Enter Age: "))
            Student_dob = input("Enter Date of Birth (DD/MM/YYYY): ")
            Student_email = input("Enter the Email: ")
            School_id = input("Enter the school ID: ")
            Class_id = input("Enter the class ID: ")
            sql_query = "INSERT INTO student(Student_name, Student_age, Student_dob, student_email, School_id, Class_id) VALUES (%s, %s, %s, %s, %s, %s);"
            parameters = (Student_name, Student_age, Student_dob, student_email, School_id, Class_id)

        elif entity == "teacher":
            name = input("Enter Teacher's Name: ")
            email = input("Enter the Email: ")
            school_id = input("Enter the school ID: ")
            sql_query = "INSERT INTO teachers (Teacher_name, Teacher_email, School_id) VALUES (%s, %s, %s);"
            parameters = (name, email, school_id)

        elif entity == "class_level":
            grade = int(input("Enter Grade: "))
            teacher_id = int(input("Enter Teacher's ID: "))
            school_id = int(input("Enter School's ID: "))
            sql_query = "INSERT INTO class_level (Grade, Teacher_id, School_id) VALUES (%s, %s, %s);"
            parameters = (grade, teacher_id, school_id)

        elif entity == "grade":
            grade_value = input("Enter Grade value: ")
            student_id = int(input("Enter Student ID: "))
            class_id = int(input("Enter Class ID: "))
            sql_query = "INSERT INTO grades (Grade_value, Student_id, Class_id) VALUES (%s, %s, %s);"
            parameters = (grade_value, student_id, class_id)

        elif entity == "events":
            name = input("Enter Event's Name: ")
            event_date = input("Enter Date (MM/DD/YYYY): ")
            location = input("Enter the location of the event: ")
            school_id = int(input("Enter the school ID: "))
            sql_query = "INSERT INTO events (Event_name, Event_date, Event_location, School_id) VALUES (%s, %s, %s, %s);"
            parameters = (name, event_date, location, school_id)

        elif entity == "facility":
            name = input("Enter the Facility Name: ")
            facility_type = input("Enter the Type of Facility: ")
            capacity = int(input("Enter the Capacity: "))
            school_id = int(input("Enter the School ID: "))
            sql_query = "INSERT INTO facility (Facility_name, Facility_type, Facility_capacity, School_id) VALUES (%s, %s, %s, %s);"
            parameters = (name, facility_type, capacity, school_id)

        elif entity == "subject":
            name = input("Enter the Subject Name: ")
            teacher_id = int(input("Enter Teacher ID: "))
            class_id = int(input("Enter Class ID: "))
            sql_query = "INSERT INTO subjects (Subject_name, Teacher_id, Class_id) VALUES (%s, %s, %s);"
            parameters = (name, teacher_id, class_id)

        else:
            print(f"Entity '{entity}' not recognized. Record not created.")

        if sql_query and parameters:
            try:
                cursor = self.connection.cursor()
                cursor.execute(sql_query, parameters)
                self.connection.commit()
                print(f"Record added successfully in {entity}.")
            except Error as e:
                print(f"Error adding record to {entity}: {e}")
            finally:
                cursor.close()
        else:
            print("No valid query to execute.")

    def display_records(self, entity):
        sql_query = f"SELECT * FROM {entity};"
        try:
            cursor = self.connection.cursor()
            cursor.execute(sql_query)
            records = cursor.fetchall()
            if records:
                column_names = [i[0] for i in cursor.description]
                print(f"\nRecords in the table '{entity}':")
                print(tabulate(records, headers=column_names, tablefmt="grid"))
            else:
                print(f"\nNo records found in the '{entity}' table.")
        except Error as e:
            print(f"Failed to retrieve records from the table {entity}: {e}")
        finally:
            cursor.close()

    def fetch_columns(self, table_name):
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(f"DESCRIBE {table_name};")
                column_info = cursor.fetchall()
                return [column[0] for column in column_info]
        except Error as err:
            print(f"Error retrieving columns for table {table_name}: {err}")
            return []

    def modify_record(self, entity):
        primary_keys = {
            "school": "school_id",
            "student": "student_id",
            "teachers": "teacher_id",
            "grades": "grade_id",
            "events": "event_id",
            "class_level": "class_id",
            "facility": "facility_id",
            "subjects": "subject_id"
        }
        primary_key = primary_keys.get(entity)
        record_id = input(f"Enter {primary_key} of the record you want to modify: ")

        columns = self.fetch_columns(entity)
        if not columns:
            print(f"Could not retrieve columns for the table {entity}.")
            return
        print("\nSelect the column to modify:")
        for i, column in enumerate(columns, 1):
            print(f"{i}. {column}")

        column_choice = int(input("Enter column number: "))
        if 1 <= column_choice <= len(columns):
            column_name = columns[column_choice - 1]
            new_value = input(f"Enter the new value for {column_name}: ")
            query = f"UPDATE {entity} SET {column_name} = %s WHERE {primary_key} = %s;"
            parameters = (new_value, record_id)

            try:
                cursor = self.connection.cursor()
                cursor.execute(query, parameters)
                self.connection.commit()
                if cursor.rowcount > 0:
                    print(f"Record updated successfully in {entity}.")
                else:
                    print("No matching record found or no update was made.")
            except Error as e:
                print(f"Error updating record in {entity}: {e}")
            finally:
                cursor.close()
        else:
            print("Invalid column choice. Please try again.")
        
    def remove_record(self, entity):
        primary_keys = {
            "school": "school_id",
            "student": "student_id",
            "teacher": "teacher_id",
            "grades": "grade_id",
            "events": "event_id",
            "class_level": "class_id",
            "facility": "facility_id",
            "subject": "subject_id"
        }

        primary_key = primary_keys.get(entity)
        record_id = input(f"Enter {primary_key} of the record you want to delete: ")

        query = f"DELETE FROM {entity} WHERE {primary_key} = %s;"
        parameters = (record_id,)

        try:
            cursor = self.connection.cursor()
            cursor.execute(query, parameters)
            self.connection.commit()
            if cursor.rowcount > 0:
                print(f"Record deleted successfully from {entity}.")
            else:
                print("No matching record found.")
        except Error as e:
            print(f"Error deleting record from {entity}: {e}")
        finally:
            cursor.close()

    def disconnect(self):
        if self.connection.is_connected():
            self.connection.close()
            print("Database connection closed.")

def create_user(db):
    new_username = input("Enter a new username: ")
    new_password = getpass.getpass("Enter a new password: ")  # Use getpass to hide input
    hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())

    try:
        cursor = db.connection.cursor()
        cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (new_username, hashed_password))
        db.connection.commit()
        print("User registered successfully!")
    except Error as e:
        print(f"Error registering user: {e}")
    finally:
        cursor.close()

def authenticate_user(db):
    username = input("Enter username: ")
    password = getpass.getpass("Enter password: ")  # Use getpass to hide input

    try:
        cursor = db.connection.cursor()
        cursor.execute("SELECT password FROM users WHERE username = %s", (username,))
        result = cursor.fetchone()

        if result and bcrypt.checkpw(password.encode('utf-8'), result[0].encode('utf-8')):
            print("Authentication successful!")
            return True
        else:
            print("Invalid username or password.")
            return False
    except Error as e:
        print(f"Error authenticating user: {e}")
    finally:
        cursor.close()
    
# Example usage
if __name__ == "__main__":
    db = DBManager("localhost", "root", "abc456", "school")


    while True:
        print("\nMenu:")
        print("1. Register a new user")
        print("2. Login")
        choice = input("Enter your choice (1-2): ")

        if choice == '1':
            create_user(db)
        elif choice == '2':
            if authenticate_user(db):
                break  # Exit the loop if login is successful
        else:
            print("Invalid choice. Please try again.")

    tables = ["school", "student", "teachers", "grades", "class_level", "events", "facility", "subjects"]
    
    while True:
        print("\nMenu:")
        print("1. Create a new record")
        print("2. Read a record")
        print("3. Update a record")
        print("4. Delete a record")
        print("5. Exit")
        choice = input("Enter your choice (1-5): ")
        
        if choice in ['1', '2', '3', '4']:
            print("\nSelect a table:")
            for i, table in enumerate(tables, 1):
                print(f"{i}. {table}")
            table_choice = int(input("Enter table number: "))
            if 1 <= table_choice <= len(tables):
                selected_table = tables[table_choice - 1]
                if choice == '1':
                    db.add_record(selected_table)
                elif choice == '2':
                    db.display_records(selected_table)
                elif choice == '3':
                    db.modify_record(selected_table)
                elif choice == '4':
                    db.remove_record(selected_table)
            else:
                print("Invalid table choice. Please try again.")
        elif choice == '5':
            db.disconnect()
            print("Exiting the application.")
            break
        else:
            print("Invalid choice. Please try again.")


