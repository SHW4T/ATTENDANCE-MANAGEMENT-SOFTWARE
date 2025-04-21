# ATTENDANCE-MANAGEMENT-SOFTWARE

A desktop-based Attendance Management System built using Python (Tkinter) and MySQL. This mini project was developed as part of the Database Systems (DBS) subject in college.

---

## Project Overview

This system allows administrators (superusers) and teachers to manage attendance efficiently. It supports user authentication, section and student management, attendance marking, reporting, and CSV export functionalities.

---

## Features

### User Authentication
- Secure login system with SHA-256 hashed passwords.
- Two user roles:
  - **Superuser (Admin):** Full access to all features.
  - **Teacher:** Access limited to assigned section.

### Section Management (Admin only)
- Add new sections.
- Remove existing sections along with all associated data (students and attendance).
- View list of all sections.

### Teacher Management (Admin only)
- Add new teachers and assign them to sections.
- Remove teachers.

### Student Management
- Add students to sections.
- Remove students from sections.
- View students in selected section.

### Attendance Management
- Mark attendance for students on a selected date.
- Automatically load attendance for the selected date.
- "Select All" and "Deselect All" options for quick marking.
- Save attendance records with timestamp and user info.

### Reporting
- View attendance report for a specific date and section.
- Export monthly attendance data as CSV files.

### User Interface
- Built with Tkinter for a simple and intuitive GUI.
- Scrollable attendance list for easy navigation.
- Date picker and quick "Today" button for convenience.

---

## Prerequisites

- Python 3.x
- MySQL Server
- Python packages:
  - `mysql-connector-python`
  - `tkinter` (usually included with Python)

---

## Setup Instructions

1. **Clone the repository:**
2. **Install dependencies:**
3. **Set up MySQL database:**

- Make sure MySQL server is running.
- Update MySQL credentials in the Python script if necessary (default is `root`/`root`).
- Run the database setup script:

  ```
  python your_script_name.py
  ```

This will create the `attendance_system` database, tables, constraints, and an initial admin user (`username: admin`, `password: admin123`).

4. **Run the application:**
   
---

## Usage

- **Login:**
- Use the admin credentials or create teacher accounts via the admin interface.
- **Manage Sections:**
- Admins can add or remove sections.
- **Manage Teachers:**
- Admins can add new teachers and assign sections.
- **Manage Students:**
- Add or remove students within a section.
- **Mark Attendance:**
- Select a section and date, mark attendance, and save.
- **View Reports:**
- Generate attendance reports for any date.
- **Export CSV:**
- Export monthly attendance data for offline use or sharing.

---

## Demo

[LinkedIn Post](https://www.linkedin.com/posts/shwat_excited-to-share-my-latest-mini-project-activity-7320072467358621696-0fzp?utm_source=share&utm_medium=member_desktop&rcm=ACoAAFheUKYBKwZZDEvvdUkR3gMmMJ6eP8me_zg)

---

## License

This project is for educational purposes and is open for modification and improvement.

---

## Acknowledgements

- Developed as a mini project for Database Systems (DBS) subject in college.
- Uses Python Tkinter for GUI and MySQL for backend database.

---

## Contact

For any queries or suggestions, please contact:

- SHASHWAT THAKUR : linkedin.com/in/shwat



