import mysql.connector
from mysql.connector import Error

def create_database_connection():
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='root'
        )
        return connection
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None

def setup_database():
    connection = create_database_connection()
    if connection:
        cursor = connection.cursor()
        
        # Create database if not exists
        cursor.execute("CREATE DATABASE IF NOT EXISTS attendance_system")
        cursor.execute("USE attendance_system")
        
        print("Creating tables without foreign keys first...")
        
        # Create tables without foreign keys initially
        tables = [
            """
            CREATE TABLE IF NOT EXISTS users (
                user_id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(50) NOT NULL UNIQUE,
                password VARCHAR(255) NOT NULL,
                is_authorized BOOLEAN DEFAULT FALSE,
                is_superuser BOOLEAN DEFAULT FALSE,
                assigned_section INT NULL
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS sections (
                section_id INT AUTO_INCREMENT PRIMARY KEY,
                section_name VARCHAR(50) NOT NULL UNIQUE,
                created_by INT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS students (
                student_id INT AUTO_INCREMENT PRIMARY KEY,
                student_name VARCHAR(100) NOT NULL,
                section_id INT,
                added_by INT,
                added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS attendance (
                attendance_id INT AUTO_INCREMENT PRIMARY KEY,
                student_id INT,
                section_id INT,
                date DATE NOT NULL,
                status BOOLEAN DEFAULT FALSE,
                marked_by INT,
                marked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE KEY unique_attendance (student_id, date)
            )
            """
        ]
        
        for table in tables:
            try:
                cursor.execute(table)
                print(f"Successfully created table")
            except Error as e:
                print(f"Error creating table: {e}")
        
        print("Adding foreign key constraints...")
        
        # Add foreign key constraints after all tables exist
        constraints = [
            """
            ALTER TABLE sections
            ADD CONSTRAINT fk_sections_created_by
            FOREIGN KEY (created_by) REFERENCES users(user_id)
            ON DELETE SET NULL
            """,
            """
            ALTER TABLE students
            ADD CONSTRAINT fk_students_section
            FOREIGN KEY (section_id) REFERENCES sections(section_id)
            ON DELETE CASCADE,
            ADD CONSTRAINT fk_students_added_by
            FOREIGN KEY (added_by) REFERENCES users(user_id)
            ON DELETE SET NULL
            """,
            """
            ALTER TABLE attendance
            ADD CONSTRAINT fk_attendance_student
            FOREIGN KEY (student_id) REFERENCES students(student_id)
            ON DELETE CASCADE,
            ADD CONSTRAINT fk_attendance_section
            FOREIGN KEY (section_id) REFERENCES sections(section_id)
            ON DELETE CASCADE,
            ADD CONSTRAINT fk_attendance_marked_by
            FOREIGN KEY (marked_by) REFERENCES users(user_id)
            ON DELETE SET NULL
            """,
            """
            ALTER TABLE users
            ADD CONSTRAINT fk_user_assigned_section
            FOREIGN KEY (assigned_section) REFERENCES sections(section_id)
            ON DELETE SET NULL
            """
        ]
        
        for constraint in constraints:
            try:
                cursor.execute(constraint)
                print("Successfully added constraint")
            except Error as e:
                print(f"Error adding constraint: {e}")
        
        # Create an initial admin user
        try:
            cursor.execute("""
                INSERT IGNORE INTO users (username, password, is_authorized, is_superuser)
                VALUES ('admin', SHA2('admin123', 256), TRUE, TRUE)
            """)
            print("Admin user created successfully")
        except Error as e:
            print(f"Error creating admin user: {e}")
        
        connection.commit()
        cursor.close()
        connection.close()
        print("Database setup completed successfully.")
    else:
        print("Failed to connect to database")

if __name__ == "__main__":
    print("Setting up database...")
    setup_database()
    print("Database setup complete.")
