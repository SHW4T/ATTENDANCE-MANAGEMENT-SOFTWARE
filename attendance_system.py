import mysql.connector
from mysql.connector import Error
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, filedialog
from datetime import datetime, date, timedelta
import csv
import calendar

class AttendanceManagementSystem:
    def __init__(self, root):
        self.root = root
        self.root.title("Attendance Management System")
        self.root.geometry("1000x700")
        
        # Database connection
        self.connection = self.create_connection()
        self.current_user = None
        
        # Login Frame
        self.login_frame = tk.Frame(self.root)
        self.login_frame.pack(pady=50)
        
        tk.Label(self.login_frame, text="Username:").grid(row=0, column=0, padx=5, pady=5)
        self.username_entry = tk.Entry(self.login_frame)
        self.username_entry.grid(row=0, column=1, padx=5, pady=5)
        
        tk.Label(self.login_frame, text="Password:").grid(row=1, column=0, padx=5, pady=5)
        self.password_entry = tk.Entry(self.login_frame, show="*")
        self.password_entry.grid(row=1, column=1, padx=5, pady=5)
        
        tk.Button(self.login_frame, text="Login", command=self.login).grid(row=2, columnspan=2, pady=10)
        
        # Main Frame (will be shown after login)
        self.main_frame = tk.Frame(self.root)
        
        # Initialize UI components that will be used after login
        self.setup_main_ui()
        
    def create_connection(self):
        try:
            connection = mysql.connector.connect(
                host='localhost',
                user='root',
                password='root',
                database='attendance_system'
            )
            return connection
        except Error as e:
            messagebox.showerror("Database Error", f"Error connecting to MySQL: {e}")
            return None
    
    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        
        if not username or not password:
            messagebox.showerror("Error", "Please enter both username and password")
            return
            
        try:
            cursor = self.connection.cursor(dictionary=True)
            cursor.execute("""
                SELECT user_id, is_superuser, assigned_section 
                FROM users 
                WHERE username = %s AND password = SHA2(%s, 256)
            """, (username, password))
            
            result = cursor.fetchone()
            if result:
                self.current_user = {
                    'user_id': result['user_id'],
                    'is_superuser': bool(result['is_superuser']),
                    'assigned_section': result['assigned_section']
                }
                
                # Hide login frame and show main frame
                self.login_frame.pack_forget()
                self.main_frame.pack(fill=tk.BOTH, expand=True)
                
                # Enable appropriate functionality based on user type
                self.enable_functionality_after_login()
                self.load_sections()
                
                # If teacher, automatically select their assigned section
                if not self.current_user['is_superuser'] and self.current_user['assigned_section']:
                    self.current_section = self.current_user['assigned_section']
                    cursor.execute("SELECT section_name FROM sections WHERE section_id = %s", 
                                 (self.current_user['assigned_section'],))
                    section_name = cursor.fetchone()['section_name']
                    self.current_section_label.config(text=f"Current Section: {section_name}")
                    self.load_students()
                    self.load_attendance()
                
            else:
                messagebox.showerror("Error", "Invalid username or password")
                
        except Error as e:
            messagebox.showerror("Database Error", f"Error during login: {e}")
    
    def setup_main_ui(self):
        # Left panel - Sections management
        left_panel = tk.Frame(self.main_frame, width=300, padx=10, pady=10, relief=tk.RIDGE, bd=2)
        left_panel.pack(side=tk.LEFT, fill=tk.Y)
        
        tk.Label(left_panel, text="Sections", font=('Arial', 12, 'bold')).pack(pady=5)
        
        # Section list
        self.section_listbox = tk.Listbox(left_panel, height=15, width=30)
        self.section_listbox.pack(pady=5)
        self.section_listbox.bind('<<ListboxSelect>>', self.on_section_select)
        
        # Section management buttons
        self.section_btn_frame = tk.Frame(left_panel)
        self.section_btn_frame.pack(pady=5)
        
        self.add_section_btn = tk.Button(self.section_btn_frame, text="Add Section", command=self.add_section)
        self.add_section_btn.grid(row=0, column=0, padx=5)
        
        self.remove_section_btn = tk.Button(self.section_btn_frame, text="Remove Section", command=self.remove_section)
        self.remove_section_btn.grid(row=0, column=1, padx=5)
        
        # Student management
        tk.Label(left_panel, text="Students", font=('Arial', 12, 'bold')).pack(pady=(10, 5))
        
        self.student_listbox = tk.Listbox(left_panel, height=15, width=30)
        self.student_listbox.pack(pady=5)
        
        self.student_btn_frame = tk.Frame(left_panel)
        self.student_btn_frame.pack(pady=5)
        
        self.add_student_btn = tk.Button(self.student_btn_frame, text="Add Student", command=self.add_student)
        self.add_student_btn.grid(row=0, column=0, padx=5)
        
        self.remove_student_btn = tk.Button(self.student_btn_frame, text="Remove Student", command=self.remove_student)
        self.remove_student_btn.grid(row=0, column=1, padx=5)
        
        # User management frame (will be populated after login if superuser)
        self.user_management_frame = tk.Frame(left_panel)
        
        # Right panel - Attendance
        right_panel = tk.Frame(self.main_frame, padx=10, pady=10, relief=tk.RIDGE, bd=2)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Date selection
        date_frame = tk.Frame(right_panel)
        date_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(date_frame, text="Date:").pack(side=tk.LEFT)
        self.date_entry = tk.Entry(date_frame)
        self.date_entry.pack(side=tk.LEFT, padx=5)
        self.date_entry.insert(0, date.today().strftime("%Y-%m-%d"))
        
        tk.Button(date_frame, text="Today", command=self.set_today_date).pack(side=tk.LEFT, padx=5)
        tk.Button(date_frame, text="Load", command=self.load_attendance).pack(side=tk.LEFT, padx=5)
        
        # Attendance frame with scrollbar
        self.attendance_container = tk.Frame(right_panel)
        self.attendance_container.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Canvas and scrollbar setup
        self.canvas = tk.Canvas(self.attendance_container)
        self.scrollbar = ttk.Scrollbar(self.attendance_container, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas)
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )
        
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        
        # Dictionary to store attendance checkboxes
        self.attendance_vars = {}
        
        # Action buttons
        btn_frame = tk.Frame(right_panel)
        btn_frame.pack(fill=tk.X, pady=5)
        
        self.save_attendance_btn = tk.Button(btn_frame, text="Save Attendance", command=self.save_attendance)
        self.save_attendance_btn.pack(side=tk.LEFT, padx=5)
        
        self.select_all_btn = tk.Button(btn_frame, text="Select All", command=self.select_all)
        self.select_all_btn.pack(side=tk.LEFT, padx=5)
        
        self.deselect_all_btn = tk.Button(btn_frame, text="Deselect All", command=self.deselect_all)
        self.deselect_all_btn.pack(side=tk.LEFT, padx=5)
        
        self.view_report_btn = tk.Button(btn_frame, text="View Report", command=self.view_report)
        self.view_report_btn.pack(side=tk.LEFT, padx=5)
        
        self.export_csv_btn = tk.Button(btn_frame, text="Export CSV", command=self.export_csv)
        self.export_csv_btn.pack(side=tk.LEFT, padx=5)
        
        self.logout_btn = tk.Button(btn_frame, text="Logout", command=self.logout)
        self.logout_btn.pack(side=tk.RIGHT, padx=5)
        
        # Current section info
        self.current_section = None
        self.current_section_label = tk.Label(right_panel, text="No section selected", font=('Arial', 10))
        self.current_section_label.pack(pady=5)
        
        # Initially disable all functionality until login
        self.disable_all_functionality()
    
    def disable_all_functionality(self):
        """Disable all functionality until user logs in"""
        self.add_section_btn.config(state=tk.DISABLED)
        self.remove_section_btn.config(state=tk.DISABLED)
        self.add_student_btn.config(state=tk.DISABLED)
        self.remove_student_btn.config(state=tk.DISABLED)
        self.section_listbox.config(state=tk.DISABLED)
        self.student_listbox.config(state=tk.DISABLED)
        self.save_attendance_btn.config(state=tk.DISABLED)
        self.select_all_btn.config(state=tk.DISABLED)
        self.deselect_all_btn.config(state=tk.DISABLED)
        self.view_report_btn.config(state=tk.DISABLED)
        self.export_csv_btn.config(state=tk.DISABLED)
        self.date_entry.config(state=tk.DISABLED)
    
    def enable_functionality_after_login(self):
        """Enable appropriate functionality based on user type after login"""
        # Clear previous user management widgets if any
        for widget in self.user_management_frame.winfo_children():
            widget.destroy()
        
        if self.current_user['is_superuser']:
            # Superuser can access everything
            self.add_section_btn.config(state=tk.NORMAL)
            self.remove_section_btn.config(state=tk.NORMAL)
            self.section_listbox.config(state=tk.NORMAL)
            
            # Add user management frame for superuser
            tk.Label(self.user_management_frame, text="User Management", font=('Arial', 12, 'bold')).pack(pady=(10, 5))
            self.user_btn_frame = tk.Frame(self.user_management_frame)
            self.user_btn_frame.pack(pady=5)
            
            tk.Button(self.user_btn_frame, text="Add Teacher", command=self.add_teacher).grid(row=0, column=0, padx=5)
            tk.Button(self.user_btn_frame, text="Remove Teacher", command=self.remove_teacher).grid(row=0, column=1, padx=5)
            
            self.user_management_frame.pack(pady=(10, 5))
        else:
            # Teacher can only access their assigned section
            if self.current_user['assigned_section']:
                self.current_section = self.current_user['assigned_section']
                self.load_students()
                self.load_attendance()
            
            # Disable section management for teachers
            self.add_section_btn.config(state=tk.DISABLED)
            self.remove_section_btn.config(state=tk.DISABLED)
            self.section_listbox.config(state=tk.DISABLED)
        
        # All logged-in users can access these
        self.add_student_btn.config(state=tk.NORMAL)
        self.remove_student_btn.config(state=tk.NORMAL)
        self.student_listbox.config(state=tk.NORMAL)
        self.save_attendance_btn.config(state=tk.NORMAL)
        self.select_all_btn.config(state=tk.NORMAL)
        self.deselect_all_btn.config(state=tk.NORMAL)
        self.view_report_btn.config(state=tk.NORMAL)
        self.export_csv_btn.config(state=tk.NORMAL)
        self.date_entry.config(state=tk.NORMAL)
    
    def load_sections(self):
        try:
            cursor = self.connection.cursor()
            
            if self.current_user['is_superuser']:
                # Superuser sees all sections
                cursor.execute("SELECT section_id, section_name FROM sections ORDER BY section_name")
            else:
                # Teacher only sees their assigned section
                cursor.execute("""
                    SELECT section_id, section_name FROM sections 
                    WHERE section_id = %s 
                    ORDER BY section_name
                """, (self.current_user['assigned_section'],))
            
            sections = cursor.fetchall()
            
            self.section_listbox.delete(0, tk.END)
            self.section_listbox.section_ids = {}
            for section in sections:
                self.section_listbox.insert(tk.END, section[1])
                self.section_listbox.section_ids[section[1]] = section[0]
                
        except Error as e:
            messagebox.showerror("Database Error", f"Error loading sections: {e}")
    
    def on_section_select(self, event):
        if self.current_user['is_superuser'] or not self.current_user['assigned_section']:
            selected = self.section_listbox.curselection()
            if selected:
                section_name = self.section_listbox.get(selected[0])
                self.current_section = self.section_listbox.section_ids[section_name]
                self.current_section_label.config(text=f"Current Section: {section_name}")
                self.load_students()
                self.load_attendance()
    
    def add_section(self):
        if not self.current_user['is_superuser']:
            messagebox.showwarning("Access Denied", "Only superusers can add sections")
            return
            
        section_name = simpledialog.askstring("Add Section", "Enter section name:")
        if section_name:
            try:
                cursor = self.connection.cursor()
                cursor.execute("""
                    INSERT INTO sections (section_name, created_by)
                    VALUES (%s, %s)
                """, (section_name, self.current_user['user_id']))
                self.connection.commit()
                self.load_sections()
                messagebox.showinfo("Success", "Section added successfully")
            except Error as e:
                messagebox.showerror("Database Error", f"Error adding section: {e}")
    
    def remove_section(self):
        if not self.current_user['is_superuser']:
            messagebox.showwarning("Access Denied", "Only superusers can remove sections")
            return
            
        selected = self.section_listbox.curselection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a section to remove")
            return
            
        section_name = self.section_listbox.get(selected[0])
        if messagebox.askyesno("Confirm", f"Are you sure you want to remove section '{section_name}' and ALL its associated data?"):
            try:
                cursor = self.connection.cursor()
                
                # First delete attendance records for this section
                cursor.execute("DELETE FROM attendance WHERE section_id = %s", 
                             (self.section_listbox.section_ids[section_name],))
                
                # Then delete students in this section
                cursor.execute("DELETE FROM students WHERE section_id = %s", 
                             (self.section_listbox.section_ids[section_name],))
                
                # Update users assigned to this section
                cursor.execute("UPDATE users SET assigned_section = NULL WHERE assigned_section = %s",
                             (self.section_listbox.section_ids[section_name],))
                
                # Finally delete the section itself
                cursor.execute("DELETE FROM sections WHERE section_id = %s", 
                             (self.section_listbox.section_ids[section_name],))
                
                self.connection.commit()
                self.load_sections()
                self.current_section = None
                self.current_section_label.config(text="No section selected")
                messagebox.showinfo("Success", "Section and all associated data removed successfully")
            except Error as e:
                self.connection.rollback()
                messagebox.showerror("Database Error", f"Error removing section: {e}")
    
    def add_teacher(self):
        if not self.current_user['is_superuser']:
            messagebox.showwarning("Access Denied", "Only superusers can add teachers")
            return
            
        username = simpledialog.askstring("Add Teacher", "Enter username for new teacher:")
        if not username:
            return
            
        password = simpledialog.askstring("Add Teacher", "Enter password for new teacher:", show="*")
        if not password:
            return
            
        # Get available sections
        cursor = self.connection.cursor()
        cursor.execute("SELECT section_id, section_name FROM sections")
        sections = cursor.fetchall()
        
        if not sections:
            messagebox.showwarning("Warning", "No sections available to assign")
            return
            
        # Create dialog to select section
        section_dialog = tk.Toplevel(self.root)
        section_dialog.title("Assign Section")
        
        tk.Label(section_dialog, text="Select section to assign:").pack(pady=5)
        
        section_var = tk.StringVar()
        section_dropdown = ttk.Combobox(section_dialog, textvariable=section_var, state="readonly")
        section_dropdown['values'] = [section[1] for section in sections]
        section_dropdown.pack(pady=5)
        
        def assign_teacher():
            selected_section_name = section_var.get()
            if not selected_section_name:
                messagebox.showwarning("Warning", "Please select a section")
                return
                
            selected_section_id = [section[0] for section in sections if section[1] == selected_section_name][0]
            
            try:
                cursor.execute("""
                    INSERT INTO users (username, password, is_superuser, assigned_section)
                    VALUES (%s, SHA2(%s, 256), FALSE, %s)
                """, (username, password, selected_section_id))
                self.connection.commit()
                messagebox.showinfo("Success", "Teacher added successfully")
                section_dialog.destroy()
            except Error as e:
                messagebox.showerror("Database Error", f"Error adding teacher: {e}")
        
        tk.Button(section_dialog, text="Assign", command=assign_teacher).pack(pady=5)
    
    def remove_teacher(self):
        if not self.current_user['is_superuser']:
            messagebox.showwarning("Access Denied", "Only superusers can remove teachers")
            return
            
        # Get all teachers
        cursor = self.connection.cursor(dictionary=True)
        cursor.execute("""
            SELECT user_id, username, assigned_section 
            FROM users 
            WHERE is_superuser = FALSE
        """)
        teachers = cursor.fetchall()
        
        if not teachers:
            messagebox.showinfo("Info", "No teachers to remove")
            return
            
        # Create dialog to select teacher
        teacher_dialog = tk.Toplevel(self.root)
        teacher_dialog.title("Remove Teacher")
        
        tk.Label(teacher_dialog, text="Select teacher to remove:").pack(pady=5)
        
        teacher_listbox = tk.Listbox(teacher_dialog, width=30, height=10)
        teacher_listbox.pack(pady=5)
        
        for teacher in teachers:
            teacher_listbox.insert(tk.END, f"{teacher['username']} (Section: {teacher['assigned_section']})")
            teacher_listbox.teacher_ids = {idx: teacher['user_id'] for idx, teacher in enumerate(teachers)}
        
        def remove_selected_teacher():
            selected = teacher_listbox.curselection()
            if not selected:
                messagebox.showwarning("Warning", "Please select a teacher to remove")
                return
                
            teacher_id = teacher_listbox.teacher_ids[selected[0]]
            
            try:
                cursor.execute("DELETE FROM users WHERE user_id = %s", (teacher_id,))
                self.connection.commit()
                messagebox.showinfo("Success", "Teacher removed successfully")
                teacher_dialog.destroy()
            except Error as e:
                messagebox.showerror("Database Error", f"Error removing teacher: {e}")
        
        tk.Button(teacher_dialog, text="Remove", command=remove_selected_teacher).pack(pady=5)
    
    def load_students(self):
        if not self.current_section:
            return
            
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                SELECT student_id, student_name 
                FROM students 
                WHERE section_id = %s 
                ORDER BY student_name
            """, (self.current_section,))
            
            students = cursor.fetchall()
            
            self.student_listbox.delete(0, tk.END)
            self.student_listbox.student_ids = {}
            for student in students:
                self.student_listbox.insert(tk.END, student[1])
                self.student_listbox.student_ids[student[1]] = student[0]
                
        except Error as e:
            messagebox.showerror("Database Error", f"Error loading students: {e}")
    
    def add_student(self):
        if not self.current_section:
            messagebox.showwarning("Warning", "Please select a section first")
            return
            
        student_name = simpledialog.askstring("Add Student", "Enter student name:")
        if student_name:
            try:
                cursor = self.connection.cursor()
                cursor.execute("""
                    INSERT INTO students (student_name, section_id, added_by)
                    VALUES (%s, %s, %s)
                """, (student_name, self.current_section, self.current_user['user_id']))
                self.connection.commit()
                self.load_students()
                messagebox.showinfo("Success", "Student added successfully")
            except Error as e:
                messagebox.showerror("Database Error", f"Error adding student: {e}")
    
    def remove_student(self):
        selected = self.student_listbox.curselection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a student to remove")
            return
            
        student_name = self.student_listbox.get(selected[0])
        if messagebox.askyesno("Confirm", f"Are you sure you want to remove student '{student_name}'?"):
            try:
                cursor = self.connection.cursor()
                cursor.execute("DELETE FROM students WHERE student_id = %s", 
                             (self.student_listbox.student_ids[student_name],))
                self.connection.commit()
                self.load_students()
                messagebox.showinfo("Success", "Student removed successfully")
            except Error as e:
                messagebox.showerror("Database Error", f"Error removing student: {e}")
    
    def set_today_date(self):
        self.date_entry.delete(0, tk.END)
        self.date_entry.insert(0, date.today().strftime("%Y-%m-%d"))
        self.load_attendance()
    
    def load_attendance(self):
        if not self.current_section:
            return
            
        try:
            # Clear previous attendance widgets
            for widget in self.scrollable_frame.winfo_children():
                widget.destroy()
            self.attendance_vars = {}
            
            # Get the date from the entry
            attendance_date = self.date_entry.get()
            datetime.strptime(attendance_date, "%Y-%m-%d")  # Validate date format
            
            # Get all students in the section
            cursor = self.connection.cursor(dictionary=True)
            cursor.execute("""
                SELECT s.student_id, s.student_name 
                FROM students s
                WHERE s.section_id = %s
                ORDER BY s.student_name
            """, (self.current_section,))
            students = cursor.fetchall()
            
            # Get attendance records for the date
            cursor.execute("""
                SELECT student_id, status 
                FROM attendance 
                WHERE section_id = %s AND date = %s
            """, (self.current_section, attendance_date))
            attendance_records = {rec['student_id']: rec['status'] for rec in cursor.fetchall()}
            
            # Create checkboxes for each student
            for student in students:
                row_frame = tk.Frame(self.scrollable_frame)
                row_frame.pack(fill=tk.X, pady=2)
                
                # Student name label
                tk.Label(row_frame, text=student['student_name'], width=30, anchor='w').pack(side=tk.LEFT)
                
                # Create and store the checkbox variable
                var = tk.BooleanVar(value=attendance_records.get(student['student_id'], False))
                self.attendance_vars[student['student_id']] = var
                
                # Create the checkbox
                tk.Checkbutton(row_frame, variable=var).pack(side=tk.RIGHT)
            
        except ValueError:
            messagebox.showerror("Error", "Invalid date format. Please use YYYY-MM-DD")
        except Error as e:
            messagebox.showerror("Database Error", f"Error loading attendance: {e}")
    
    def select_all(self):
        for var in self.attendance_vars.values():
            var.set(True)
    
    def deselect_all(self):
        for var in self.attendance_vars.values():
            var.set(False)
    
    def save_attendance(self):
        if not self.current_section:
            messagebox.showwarning("Warning", "Please select a section first")
            return
            
        try:
            attendance_date = self.date_entry.get()
            datetime.strptime(attendance_date, "%Y-%m-%d")  # Validate date format
            
            cursor = self.connection.cursor()
            
            for student_id, var in self.attendance_vars.items():
                status = var.get()
                cursor.execute("""
                    INSERT INTO attendance (student_id, section_id, date, status, marked_by)
                    VALUES (%s, %s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE status = %s, marked_by = %s, marked_at = CURRENT_TIMESTAMP
                """, (
                    student_id, 
                    self.current_section, 
                    attendance_date, 
                    status,
                    self.current_user['user_id'],
                    status,
                    self.current_user['user_id']
                ))
            
            self.connection.commit()
            messagebox.showinfo("Success", "Attendance saved successfully")
            
        except ValueError:
            messagebox.showerror("Error", "Invalid date format. Please use YYYY-MM-DD")
        except Error as e:
            messagebox.showerror("Database Error", f"Error saving attendance: {e}")
    
    def view_report(self):
        if not self.current_section:
            messagebox.showwarning("Warning", "Please select a section first")
            return
            
        try:
            # Get section name
            cursor = self.connection.cursor()
            cursor.execute("SELECT section_name FROM sections WHERE section_id = %s", (self.current_section,))
            section_name = cursor.fetchone()[0]
            
            # Get the date from the entry
            attendance_date = self.date_entry.get()
            datetime.strptime(attendance_date, "%Y-%m-%d")  # Validate date format
            
            # Create a new window for the report
            report_window = tk.Toplevel(self.root)
            report_window.title(f"Attendance Report - {section_name} - {attendance_date}")
            report_window.geometry("600x400")
            
            # Treeview for the report
            report_tree = ttk.Treeview(report_window, columns=('id', 'name', 'status'), show='headings')
            report_tree.heading('id', text='ID')
            report_tree.heading('name', text='Name')
            report_tree.heading('status', text='Status')
            report_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            
            # Get attendance data
            cursor = self.connection.cursor(dictionary=True)
            cursor.execute("""
                SELECT s.student_id, s.student_name, 
                       IFNULL(a.status, FALSE) AS status
                FROM students s
                LEFT JOIN attendance a ON s.student_id = a.student_id 
                    AND a.section_id = s.section_id 
                    AND a.date = %s
                WHERE s.section_id = %s
                ORDER BY s.student_name
            """, (attendance_date, self.current_section))
            
            for student in cursor.fetchall():
                report_tree.insert('', tk.END, values=(
                    student['student_id'],
                    student['student_name'],
                    'Present' if student['status'] else 'Absent'
                ))
            
        except ValueError:
            messagebox.showerror("Error", "Invalid date format. Please use YYYY-MM-DD")
        except Error as e:
            messagebox.showerror("Database Error", f"Error generating report: {e}")
    
    def export_csv(self):
        if not self.current_section:
            messagebox.showwarning("Warning", "Please select a section first")
            return
            
        try:
            # Get section name
            cursor = self.connection.cursor()
            cursor.execute("SELECT section_name FROM sections WHERE section_id = %s", (self.current_section,))
            section_name = cursor.fetchone()[0]
            
            # Get the month and year from the date entry
            attendance_date = self.date_entry.get()
            date_obj = datetime.strptime(attendance_date, "%Y-%m-%d")
            month = date_obj.month
            year = date_obj.year
            
            # Get first and last day of the month
            first_day = date(year, month, 1)
            last_day = date(year, month, calendar.monthrange(year, month)[1])
            
            # Get all students in the section
            cursor.execute("""
                SELECT student_id, student_name 
                FROM students 
                WHERE section_id = %s 
                ORDER BY student_name
            """, (self.current_section,))
            students = cursor.fetchall()
            
            # Get attendance data for the month
            cursor.execute("""
                SELECT student_id, date as attendance_date, status 
                FROM attendance 
                WHERE section_id = %s 
                AND date BETWEEN %s AND %s
            """, (self.current_section, first_day, last_day))
            
            # Create a dictionary of attendance records
            attendance_data = {}
            for row in cursor:
                student_id = row[0]
                att_date = row[1]  # Changed variable name from 'date' to 'att_date'
                status = row[2]
                if student_id not in attendance_data:
                    attendance_data[student_id] = {}
                attendance_data[student_id][att_date] = status
            
            # Ask for file location
            file_path = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv")],
                initialfile=f"attendance_{section_name}_{year}_{month}.csv"
            )
            
            if not file_path:
                return  # User cancelled
            
            # Write CSV file
            with open(file_path, 'w', newline='') as csvfile:
                writer = csv.writer(csvfile)
                
                # Write header row
                headers = ['Student ID', 'Name']
                current_day = first_day
                while current_day <= last_day:
                    headers.append(current_day.strftime("%Y-%m-%d"))
                    current_day += timedelta(days=1)
                writer.writerow(headers)
                
                # Write data rows
                for student_id, student_name in students:
                    row = [student_id, student_name]
                    current_day = first_day
                    while current_day <= last_day:
                        status = attendance_data.get(student_id, {}).get(current_day, False)
                        row.append('P' if status else 'A')
                        current_day += timedelta(days=1)
                    writer.writerow(row)
            
            messagebox.showinfo("Success", f"CSV file exported successfully to:\n{file_path}")
            
        except ValueError:
            messagebox.showerror("Error", "Invalid date format. Please use YYYY-MM-DD")
        except Error as e:
            messagebox.showerror("Database Error", f"Error exporting CSV: {e}")
        except Exception as e:
            messagebox.showerror("Error", f"Error writing CSV file: {str(e)}")
    
    def logout(self):
        self.main_frame.pack_forget()
        self.login_frame.pack(pady=50)
        self.current_user = None
        self.current_section = None
        self.username_entry.delete(0, tk.END)
        self.password_entry.delete(0, tk.END)
        self.disable_all_functionality()

if __name__ == "__main__":
    root = tk.Tk()
    app = AttendanceManagementSystem(root)
    root.mainloop()
