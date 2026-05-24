import streamlit as st
import datetime
import sqlite3
import smtplib
from email.message import EmailMessage
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from io import BytesIO
import base64

# Page configuration
st.set_page_config(
    page_title="Hospital Management System",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        padding: 1rem;
        background: linear-gradient(90deg, #e3f2fd 0%, #bbdefb 100%);
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    .success-box {
        padding: 1rem;
        background-color: #d4edda;
        border-left: 5px solid #28a745;
        border-radius: 5px;
        margin: 1rem 0;
    }
    .error-box {
        padding: 1rem;
        background-color: #f8d7da;
        border-left: 5px solid #dc3545;
        border-radius: 5px;
        margin: 1rem 0;
    }
    .data-table {
        width: 100%;
        border-collapse: collapse;
        margin: 1rem 0;
    }
    .data-table th {
        background-color: #1f77b4;
        color: white;
        padding: 12px;
        text-align: left;
        font-weight: bold;
    }
    .data-table td {
        padding: 10px;
        border-bottom: 1px solid #ddd;
    }
    .data-table tr:hover {
        background-color: #f5f5f5;
    }
    .bill-container {
        background-color: white;
        padding: 30px;
        border-radius: 10px;
        box-shadow: 0 0 20px rgba(0,0,0,0.1);
        margin: 20px 0;
        font-family: 'Arial', sans-serif;
    }
    .bill-header {
        text-align: center;
        border-bottom: 2px solid #1f77b4;
        padding-bottom: 20px;
        margin-bottom: 20px;
    }
    .bill-header h1 {
        color: #1f77b4;
        font-size: 32px;
        margin: 0;
        font-weight: bold;
    }
    .bill-header h3 {
        color: #666;
        margin: 5px 0;
    }
    .bill-header p {
        color: #888;
        margin: 2px 0;
    }
    .bill-info {
        background-color: #f8f9fa;
        padding: 15px;
        border-radius: 5px;
        margin-bottom: 20px;
        border-left: 4px solid #1f77b4;
    }
    .bill-table {
        width: 100%;
        border-collapse: collapse;
        margin: 20px 0;
    }
    .bill-table th {
        background-color: #1f77b4;
        color: white;
        padding: 12px;
        text-align: left;
        font-weight: bold;
        border: 1px solid #ddd;
    }
    .bill-table td {
        padding: 10px;
        border: 1px solid #ddd;
    }
    .bill-table tr:nth-child(even) {
        background-color: #f8f9fa;
    }
    .bill-table tr:hover {
        background-color: #f1f1f1;
    }
    .summary-box {
        background-color: #e8f4f8;
        padding: 20px;
        border-radius: 5px;
        margin: 20px 0;
        border: 1px solid #1f77b4;
    }
    .terms-box {
        background-color: #fff3cd;
        padding: 15px;
        border-radius: 5px;
        margin: 20px 0;
        border-left: 4px solid #ffc107;
        font-size: 14px;
    }
    .footer {
        text-align: center;
        margin-top: 30px;
        padding-top: 20px;
        border-top: 1px dashed #ccc;
        color: #666;
    }
    .amount-words {
        font-size: 18px;
        font-weight: bold;
        color: #28a745;
        padding: 10px;
        background-color: #d4edda;
        border-radius: 5px;
        margin: 20px 0;
        text-align: center;
    }
    .payment-info {
        background-color: #e3f2fd;
        padding: 20px;
        border-radius: 5px;
        margin: 20px 0;
        border: 1px solid #1f77b4;
    }
    .patient-card {
        background-color: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        margin: 20px 0;
        border-left: 5px solid #1f77b4;
    }
    .patient-header {
        background-color: #1f77b4;
        color: white;
        padding: 10px;
        border-radius: 5px 5px 0 0;
        margin: -20px -20px 20px -20px;
    }
    .info-grid {
        display: grid;
        grid-template-columns: repeat(2, 1fr);
        gap: 15px;
    }
    .info-item {
        padding: 10px;
        background-color: #f8f9fa;
        border-radius: 5px;
    }
    .info-label {
        font-weight: bold;
        color: #1f77b4;
        font-size: 14px;
    }
    .info-value {
        font-size: 16px;
        margin-top: 5px;
    }
    </style>
""", unsafe_allow_html=True)

# python code for hospital management system

class HospitalManagementSystem:
    def __init__(self):
        self.admin_password = "admin123"
        self.init_database()
        
    def init_database(self):
        """Initialize SQLite database"""
        self.conn = sqlite3.connect('hospital_management.db', check_same_thread=False)
        self.cursor = self.conn.cursor()
        
        # Create doctors table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS doctors (
                doc_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                specialization TEXT NOT NULL,
                phone TEXT NOT NULL
            )
        ''')
        
        # Create patients table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS patients (
                patient_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                age TEXT NOT NULL,
                gender TEXT NOT NULL,
                phone TEXT NOT NULL,
                address TEXT NOT NULL,
                email TEXT NOT NULL,
                status TEXT DEFAULT 'Admitted',
                total_charges REAL DEFAULT 0
            )
        ''')
        
        # Create appointments table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS appointments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_id TEXT NOT NULL,
                patient_name TEXT NOT NULL,
                doctor_id TEXT NOT NULL,
                doctor_name TEXT NOT NULL,
                date TEXT NOT NULL,
                time TEXT NOT NULL,
                FOREIGN KEY (patient_id) REFERENCES patients(patient_id),
                FOREIGN KEY (doctor_id) REFERENCES doctors(doc_id)
            )
        ''')
        
        # Create counters table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS counters (
                name TEXT PRIMARY KEY,
                value INTEGER NOT NULL
            )
        ''')
        
        self.conn.commit()
    
    def get_counter(self, name):
        """Get counter value"""
        self.cursor.execute("SELECT value FROM counters WHERE name = ?", (name,))
        result = self.cursor.fetchone()
        return result[0] if result else 1
    
    def save_counter(self, name, value):
        """Save counter to database"""
        self.cursor.execute('''
            INSERT OR REPLACE INTO counters (name, value)
            VALUES (?, ?)
        ''', (name, value))
        self.conn.commit()
    
    def validate_phone(self, phone):
        """Validate phone number"""
        return phone.isdigit() and len(phone) == 10
    
    def generate_doctor_id(self):
        """Generate doctor ID"""
        counter = self.get_counter('doctor_counter')
        doc_id = f"DOC{counter:03d}"
        self.save_counter('doctor_counter', counter + 1)
        return doc_id
    
    def generate_patient_id(self):
        """Generate patient ID"""
        counter = self.get_counter('patient_counter')
        pat_id = f"PAT{counter:03d}"
        self.save_counter('patient_counter', counter + 1)
        return pat_id
    
    def add_doctor(self, name, specialization, phone):
        """Add new doctor"""
        doc_id = self.generate_doctor_id()
        self.cursor.execute('''
            INSERT INTO doctors (doc_id, name, specialization, phone)
            VALUES (?, ?, ?, ?)
        ''', (doc_id, name, specialization, phone))
        self.conn.commit()
        return doc_id
    
    def get_all_doctors(self):
        """Get all doctors"""
        self.cursor.execute("SELECT doc_id, name, specialization, phone FROM doctors")
        return self.cursor.fetchall()
    
    def search_doctor(self, doc_id):
        """Search doctor by ID"""
        self.cursor.execute("SELECT doc_id, name, specialization, phone FROM doctors WHERE doc_id = ?", (doc_id,))
        return self.cursor.fetchone()
    
    def remove_doctor(self, doc_id):
        """Remove doctor from database"""
        self.cursor.execute("DELETE FROM doctors WHERE doc_id = ?", (doc_id,))
        self.conn.commit()
        return self.cursor.rowcount > 0
    
    def register_patient(self, name, age, gender, phone, address, email):
        """Register new patient"""
        patient_id = self.generate_patient_id()
        self.cursor.execute('''
            INSERT INTO patients (patient_id, name, age, gender, phone, address, email, status, total_charges)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (patient_id, name, age, gender, phone, address, email, 'Admitted', 0))
        self.conn.commit()
        return patient_id
    
    def get_all_patients(self):
        """Get all patients"""
        self.cursor.execute("SELECT patient_id, name, age, gender, phone, status FROM patients")
        return self.cursor.fetchall()
    
    def search_patient(self, patient_id):
        """Search patient by ID"""
        self.cursor.execute("SELECT * FROM patients WHERE patient_id = ?", (patient_id,))
        return self.cursor.fetchone()
    
    def discharge_patient(self, patient_id):
        """Discharge patient"""
        self.cursor.execute("UPDATE patients SET status = 'Discharged' WHERE patient_id = ?", (patient_id,))
        self.conn.commit()
    
    def book_appointment(self, patient_id, doctor_id, date, time):
        """Book appointment"""
        # Get patient and doctor names
        patient = self.search_patient(patient_id)
        doctor = self.search_doctor(doctor_id)
        
        if patient and doctor:
            self.cursor.execute('''
                INSERT INTO appointments (patient_id, patient_name, doctor_id, doctor_name, date, time)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (patient_id, patient[1], doctor_id, doctor[1], date, time))
            self.conn.commit()
            return True
        return False
    
    def get_all_appointments(self):
        """Get all appointments"""
        self.cursor.execute("SELECT patient_id, patient_name, doctor_name, date, time FROM appointments")
        return self.cursor.fetchall()
    
    def update_patient_charges(self, patient_id, total_charges):
        """Update patient charges"""
        self.cursor.execute("UPDATE patients SET total_charges = ? WHERE patient_id = ?", (total_charges, patient_id))
        self.conn.commit()
    
    def generate_html_bill(self, bill):
        """Generate HTML bill content for email"""
        # Create services table HTML
        services_rows = ""
        for idx, (service, amount) in enumerate(bill['services'], 1):
            services_rows += f"""
                <tr>
                    <td style='padding: 10px; border: 1px solid #ddd; text-align: center;'>{idx}</td>
                    <td style='padding: 10px; border: 1px solid #ddd;'>{service}</td>
                    <td style='padding: 10px; border: 1px solid #ddd; text-align: right;'>₹{amount:,.2f}</td>
                </tr>
            """
        
        # Calculate tax components
        cgst = bill['tax'] / 2
        sgst = bill['tax'] / 2
        
        # Generate complete HTML bill
        html_bill = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                body {{
                    font-family: 'Arial', sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 800px;
                    margin: 0 auto;
                    padding: 20px;
                }}
                .bill-container {{
                    background-color: white;
                    padding: 30px;
                    border-radius: 10px;
                    box-shadow: 0 0 20px rgba(0,0,0,0.1);
                }}
                .bill-header {{
                    text-align: center;
                    border-bottom: 2px solid #1f77b4;
                    padding-bottom: 20px;
                    margin-bottom: 20px;
                }}
                .bill-header h1 {{
                    color: #1f77b4;
                    font-size: 32px;
                    margin: 0;
                    font-weight: bold;
                }}
                .bill-header h3 {{
                    color: #666;
                    margin: 5px 0;
                }}
                .bill-header p {{
                    color: #888;
                    margin: 2px 0;
                }}
                .bill-info {{
                    background-color: #f8f9fa;
                    padding: 15px;
                    border-radius: 5px;
                    margin-bottom: 20px;
                    border-left: 4px solid #1f77b4;
                }}
                .bill-info table {{
                    width: 100%;
                }}
                .patient-details {{
                    background-color: #f1f1f1;
                    padding: 15px;
                    border-radius: 5px;
                    margin: 20px 0;
                }}
                .patient-details h4 {{
                    color: #1f77b4;
                    margin-top: 0;
                }}
                .services-table {{
                    width: 100%;
                    border-collapse: collapse;
                    margin: 20px 0;
                }}
                .services-table th {{
                    background-color: #1f77b4;
                    color: white;
                    padding: 12px;
                    text-align: left;
                    font-weight: bold;
                    border: 1px solid #ddd;
                }}
                .services-table td {{
                    padding: 10px;
                    border: 1px solid #ddd;
                }}
                .services-table tr:nth-child(even) {{
                    background-color: #f8f9fa;
                }}
                .summary-box {{
                    background-color: #e8f4f8;
                    padding: 20px;
                    border-radius: 5px;
                    margin: 20px 0;
                    border: 1px solid #1f77b4;
                }}
                .summary-grid {{
                    display: grid;
                    grid-template-columns: 1fr 1fr 1fr;
                    gap: 20px;
                }}
                .total-box {{
                    background-color: #1f77b4;
                    color: white;
                    padding: 15px;
                    border-radius: 5px;
                }}
                .total-box strong {{
                    display: block;
                    margin-bottom: 5px;
                }}
                .total-box span {{
                    font-size: 24px;
                    font-weight: bold;
                }}
                .amount-words {{
                    font-size: 18px;
                    font-weight: bold;
                    color: #28a745;
                    padding: 15px;
                    background-color: #d4edda;
                    border-radius: 5px;
                    margin: 20px 0;
                    text-align: center;
                }}
                .payment-info {{
                    background-color: #e3f2fd;
                    padding: 20px;
                    border-radius: 5px;
                    margin: 20px 0;
                    border: 1px solid #1f77b4;
                }}
                .terms-box {{
                    background-color: #fff3cd;
                    padding: 15px;
                    border-radius: 5px;
                    margin: 20px 0;
                    border-left: 4px solid #ffc107;
                    font-size: 14px;
                }}
                .footer {{
                    text-align: center;
                    margin-top: 30px;
                    padding-top: 20px;
                    border-top: 1px dashed #ccc;
                    color: #666;
                }}
            </style>
        </head>
        <body>
            <div class="bill-container">
                <!-- Header -->
                <div class="bill-header">
                    <h1>🏥 LJ HOSPITAL & MEDICAL CENTER</h1>
                    <h3>Complete Healthcare Solutions</h3>
                    <p>LJ Campus, Makarba, Ahmedabad, Gujarat, 382210</p>
                    <p>📞 +91-9924822196 | 📧 accounts@ljhospital.com | 🌐 www.ljhospital.com</p>
                    <p>GSTIN: 27ABCDE1234F1Z5 | CIN: U85110MH2020PTC123456</p>
                </div>
                
                <!-- Bill Title -->
                <div style="text-align: center; margin: 20px 0;">
                    <h2 style="color: #1f77b4; border-bottom: 2px solid #1f77b4; display: inline-block; padding-bottom: 10px;">TAX INVOICE / BILL</h2>
                </div>
                
                <!-- Bill Information -->
                <div class="bill-info">
                    <table>
                        <tr>
                            <td><strong>Bill No:</strong> {bill['bill_no']}</td>
                            <td><strong>Bill Date:</strong> {bill['bill_date']}</td>
                            <td><strong>Due Date:</strong> {bill['due_date']}</td>
                        </tr>
                        <tr>
                            <td><strong>Payment Terms:</strong> Due on receipt</td>
                            <td><strong>Mode:</strong> Cash/Card/UPI</td>
                            <td><strong>Reference:</strong> {bill['patient_id']}</td>
                        </tr>
                    </table>
                </div>
                
                <!-- Patient Details -->
                <div class="patient-details">
                    <h4>👤 PATIENT DETAILS</h4>
                    <table style="width: 100%;">
                        <tr>
                            <td><strong>Patient Name:</strong> {bill['patient_name']}</td>
                            <td><strong>Patient ID:</strong> {bill['patient_id']}</td>
                        </tr>
                        <tr>
                            <td><strong>Phone:</strong> {bill['patient_phone']}</td>
                            <td><strong>Email:</strong> {bill['patient_email']}</td>
                        </tr>
                        <tr>
                            <td colspan="2"><strong>Address:</strong> {bill['patient_address'][:100]}</td>
                        </tr>
                    </table>
                </div>
                
                <!-- Services Table -->
                <h4 style="color: #1f77b4;">📋 SERVICE DETAILS</h4>
                <table class="services-table">
                    <thead>
                        <tr>
                            <th style="width: 10%;">S.No.</th>
                            <th style="width: 60%;">Description</th>
                            <th style="width: 30%; text-align: right;">Amount (₹)</th>
                        </tr>
                    </thead>
                    <tbody>
                        {services_rows}
                    </tbody>
                </table>
                
                <!-- Summary -->
                <div class="summary-box">
                    <h4 style="color: #1f77b4; margin-top: 0;">💰 CHARGE SUMMARY</h4>
                    <div class="summary-grid">
                        <div>
                            <p><strong>Subtotal:</strong> ₹{bill['subtotal']:,.2f}</p>
                            <p><strong>Discount ({bill['discount']:.1f}%):</strong> <span style="color: red;">-₹{bill['discount_amount']:,.2f}</span></p>
                            <p><strong>Taxable Amount:</strong> ₹{bill['taxable_amount']:,.2f}</p>
                        </div>
                        <div>
                            <p><strong>CGST (2.5%):</strong> ₹{cgst:,.2f}</p>
                            <p><strong>SGST (2.5%):</strong> ₹{sgst:,.2f}</p>
                            <p><strong>Total Tax:</strong> ₹{bill['tax']:,.2f}</p>
                        </div>
                        <div class="total-box">
                            <strong>Total Amount:</strong> ₹{bill['total']:,.2f}
                            <strong>Advance Paid:</strong> ₹{bill['advance_paid']:,.2f}
                            <strong>Balance Due:</strong> <span>₹{bill['balance_due']:,.2f}</span>
                        </div>
                    </div>
                </div>
                
                <!-- Amount in Words -->
                <div class="amount-words">
                    <strong>Amount in Words:</strong> {number_to_words(bill['total'])}
                </div>
                
                <!-- Payment Options -->
                <div class="payment-info">
                    <h4 style="color: #1f77b4; margin-top: 0;">💳 Payment Options</h4>
                    <div>
                        <p><strong>UPI ID:</strong> ljhospital@okhdfcbank</p>
                        <p><strong>Bank:</strong> HDFC Bank, Medical Branch</p>
                        <p><strong>Account:</strong> 50100234567890 | <strong>IFSC:</strong> HDFC0001234</p>
                        <p><strong>Cash/Card payments accepted at counter</strong></p>
                    </div>
                </div>
                
                <!-- Terms and Conditions -->
                <div class="terms-box">
                    <h4 style="color: #856404; margin-top: 0;">📝 TERMS & CONDITIONS</h4>
                    <ol style="margin-bottom: 0;">
                        <li>This is a computer generated invoice - valid without signature</li>
                        <li>Payment is due within 15 days of bill date</li>
                        <li>Late payment may attract interest @ 18% per annum</li>
                        <li>For any queries, contact billing department at accounts@ljhospital.com</li>
                        <li>Insurance claims to be submitted within 7 days of discharge</li>
                        <li>This bill includes all applicable taxes as per GST rules</li>
                    </ol>
                </div>
                
                <!-- Footer -->
                <div class="footer">
                    <p><strong>Thank you for choosing LJ Hospital. Wishing you good health!</strong> 🌟</p>
                    <p style="font-size: 12px; color: #999;">This is a system generated bill - no signature required</p>
                    <p style="font-size: 12px; color: #999;">Bill generated on: {datetime.datetime.now().strftime("%d-%m-%Y %I:%M %p")}</p>
                </div>
            </div>
        </body>
        </html>
        """
        return html_bill
    
    def send_bill_email(self, patient_email, bill, patient_name, total_amount):
        """Send bill via email with HTML formatting"""
        try:
            # Email configuration
            sender_email = "vrajkoladiya4786@gmail.com"
            sender_password = "zxka kgyf vxnc ucss"
            
            # Create message container
            msg = MIMEMultipart('alternative')
            msg['Subject'] = f'LJ Hospital - Bill for {patient_name}'
            msg['From'] = sender_email
            msg['To'] = patient_email
            
            # Create plain text version
            text_content = f"""Dear {patient_name},

Thank you for choosing LJ Hospital.

Your bill details:
Total Amount: ₹{total_amount:,.2f}

Bill No: {bill['bill_no']}
Bill Date: {bill['bill_date']}
Due Date: {bill['due_date']}

Services:
"""
            for s, a in bill['services']:
                text_content += f"\n{s}: ₹{a:,.2f}"
            
            text_content += f"""

Subtotal: ₹{bill['subtotal']:,.2f}
Discount ({bill['discount']}%): -₹{bill['discount_amount']:,.2f}
Tax (5%): ₹{bill['tax']:,.2f}
Total Amount: ₹{bill['total']:,.2f}
Advance Paid: ₹{bill['advance_paid']:,.2f}
Balance Due: ₹{bill['balance_due']:,.2f}

Best regards,
LJ Hospital
Phone: +91-9924822196

---
This is an automated email. Please do not reply to this message.
"""
            
            # Create HTML version
            html_content = self.generate_html_bill(bill)
            
            # Attach both versions
            msg.attach(MIMEText(text_content, 'plain'))
            msg.attach(MIMEText(html_content, 'html'))
            
            # Send email using SMTP
            with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
                smtp.login(sender_email, sender_password)
                smtp.send_message(msg)
            
            return True
            
        except smtplib.SMTPAuthenticationError:
            st.error("❌ Email authentication failed. Please check your email credentials or use an App Password.")
            st.info("💡 To fix this: Go to Google Account → Security → 2-Step Verification → App Passwords → Generate new app password")
            return False
        except smtplib.SMTPException as e:
            st.error(f"❌ SMTP error occurred: {str(e)}")
            return False
        except Exception as e:
            st.error(f"❌ Email sending failed: {str(e)}")
            st.info("💡 Please verify: 1) Internet connection, 2) Email credentials, 3) Recipient email address")
            return False

def display_table(headers, data):
    """Display data in HTML table format"""
    if not data:
        st.info("No records found.")
        return
    
    table_html = "<table class='data-table'><thead><tr>"
    
    # Add headers
    for header in headers:
        table_html += f"<th>{header}</th>"
    table_html += "</tr></thead><tbody>"
    
    # Add data rows
    for row in data:
        table_html += "<tr>"
        for cell in row:
            table_html += f"<td>{cell}</td>"
        table_html += "</tr>"
    
    table_html += "</tbody></table>"
    st.markdown(table_html, unsafe_allow_html=True)

def number_to_words(num):
    """Convert number to words"""
    if num == 0:
        return "Zero"
    
    ones = ["", "One", "Two", "Three", "Four", "Five", "Six", "Seven", "Eight", "Nine",
            "Ten", "Eleven", "Twelve", "Thirteen", "Fourteen", "Fifteen", "Sixteen",
            "Seventeen", "Eighteen", "Nineteen"]
    tens = ["", "", "Twenty", "Thirty", "Forty", "Fifty", "Sixty", "Seventy", "Eighty", "Ninety"]
    
    def convert_two_digits(n):
        if n < 20:
            return ones[n]
        else:
            return tens[n // 10] + ("" if n % 10 == 0 else " " + ones[n % 10])
    
    def convert_three_digits(n):
        if n < 100:
            return convert_two_digits(n)
        else:
            return ones[n // 100] + " Hundred" + ("" if n % 100 == 0 else " and " + convert_two_digits(n % 100))
    
    # Convert the integer part
    rupees = int(num)
    paise = round((num - rupees) * 100)
    
    if rupees == 0:
        rupees_words = "Zero"
    elif rupees < 1000:
        rupees_words = convert_three_digits(rupees)
    elif rupees < 100000:
        rupees_words = convert_two_digits(rupees // 1000) + " Thousand" + ("" if rupees % 1000 == 0 else " " + convert_three_digits(rupees % 1000))
    elif rupees < 10000000:
        rupees_words = convert_two_digits(rupees // 100000) + " Lakh" + ("" if rupees % 100000 == 0 else " " + convert_three_digits(rupees % 100000))
    else:
        rupees_words = convert_two_digits(rupees // 10000000) + " Crore" + ("" if rupees % 10000000 == 0 else " " + convert_three_digits(rupees % 10000000))
    
    if paise > 0:
        return f"Rupees {rupees_words} and {convert_two_digits(paise)} Paise Only"
    else:
        return f"Rupees {rupees_words} Only"

# Initialize session state
if 'hms' not in st.session_state:
    st.session_state.hms = HospitalManagementSystem()
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'page' not in st.session_state:
    st.session_state.page = "Home"
if 'bill_generated' not in st.session_state:
    st.session_state.bill_generated = False
if 'current_bill' not in st.session_state:
    st.session_state.current_bill = None

hms = st.session_state.hms

# Login Page
if not st.session_state.authenticated:
    st.markdown("<h1 class='main-header'> 🏥 City Hospital Management System</h1>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("### 🔐 Admin Login")
        password = st.text_input("Enter Admin Password", type="password", key="login_password")
        
        if st.button("Login", use_container_width=True):
            if password == hms.admin_password:
                st.session_state.authenticated = True
                st.success("✓ Access granted! Welcome to the system.")
                st.rerun()
            else:
                st.error("✗ Incorrect password. Access denied.")
else:
    # Sidebar Navigation
    st.sidebar.title("🏥 HMS Navigation")
    
    page = st.sidebar.radio(
        "Select Module",
        ["Home", " 👨‍⚕️ Doctor Management", " 👥 Patient Management", " 📊 Reports", " ⚙️ Settings"]
    )
    
    if st.sidebar.button("🚪 Logout", use_container_width=True):
        st.session_state.authenticated = False
        st.rerun()
    
    # Home Page
    if page == "Home":
        st.markdown("<h1 class='main-header'> 🏥 City Hospital Management System</h1>", unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("👨‍⚕️ Total Doctors", len(hms.get_all_doctors()))
        with col2:
            st.metric("👥 Total Patients", len(hms.get_all_patients()))
        with col3:
            st.metric("📅 Total Appointments", len(hms.get_all_appointments()))
        
        st.markdown("---")
        st.info("👈 Use the sidebar to navigate through different modules")
    
    # Doctor Management
    elif page == " 👨‍⚕️ Doctor Management":
        st.title("👨‍⚕️ Doctor Management")
        
        tab1, tab2, tab3, tab4, tab5 = st.tabs(["➕ Add Doctor", "📋 View Doctors", "🔍 Search Doctor", "🗑️ Remove Doctor", "📅 View Appointments"])
        
        with tab1:
            st.subheader("Register New Doctor")
            with st.form("add_doctor_form"):
                name = st.text_input("Doctor's Full Name")
                specialization = st.text_input("Specialization")
                phone = st.text_input("Contact Number (10 digits)")
                
                submitted = st.form_submit_button("Register Doctor")
                
                if submitted:
                    if not name or not specialization or not phone:
                        st.error("❌ All fields are required!")
                    elif not hms.validate_phone(phone):
                        st.error("❌ Invalid phone number! Please enter exactly 10 digits.")
                    else:
                        doc_id = hms.add_doctor(name, specialization, phone)
                        st.success(f"✅ Dr. {name} has been successfully registered with ID: {doc_id}")
        
        with tab2:
            st.subheader("Registered Doctors Directory")
            doctors = hms.get_all_doctors()
            display_table(["ID", "Name", "Specialization", "Phone"], doctors)
        
        with tab3:
            st.subheader("Search for a Doctor")
            search_option = st.radio("Search by:", ["Doctor ID", "Doctor Name"], horizontal=True)
            
            if search_option == "Doctor ID":
                doc_id = st.text_input("Enter Doctor ID")
                if st.button("🔍 Search"):
                    doctor = hms.search_doctor(doc_id)
                    if doctor:
                        st.success("✅ Doctor Found!")
                        col1, col2 = st.columns(2)
                        with col1:
                            st.write(f"**Doctor ID:** {doctor[0]}")
                            st.write(f"**Full Name:** {doctor[1]}")
                        with col2:
                            st.write(f"**Specialization:** {doctor[2]}")
                            st.write(f"**Phone:** {doctor[3]}")
                    else:
                        st.error("✗ No doctor found with this ID.")
            else:  # Search by name
                doc_name = st.text_input("Enter Doctor Name to search")
                if st.button("🔍 Search by Name"):
                    if doc_name:
                        # Get all doctors and filter by name (case-insensitive partial match)
                        all_doctors = hms.get_all_doctors()
                        matching_doctors = [doc for doc in all_doctors if doc_name.lower() in doc[1].lower()]
                        
                        if matching_doctors:
                            st.success(f"✅ Found {len(matching_doctors)} doctor(s) matching '{doc_name}'")
                            display_table(["ID", "Name", "Specialization", "Phone"], matching_doctors)
                        else:
                            st.error(f"✗ No doctors found with name containing '{doc_name}'")
                    else:
                        st.warning("⚠️ Please enter a doctor name to search")
        
        with tab4:
            st.subheader("Remove Doctor")
            st.warning("⚠️ Warning: Removing a doctor will permanently delete their record from the system.")
            
            search_option = st.radio("Search doctor by:", ["Doctor ID", "Doctor Name"], horizontal=True, key="remove_search_option")
            
            if search_option == "Doctor ID":
                doc_id = st.text_input("Enter Doctor ID to remove", key="remove_doc_id")
                
                if st.button("🔍 Search Doctor", key="search_by_id_for_removal"):
                    if doc_id:
                        doctor = hms.search_doctor(doc_id)
                        if doctor:
                            st.success("✅ Doctor Found!")
                            col1, col2 = st.columns(2)
                            with col1:
                                st.write(f"**Doctor ID:** {doctor[0]}")
                                st.write(f"**Full Name:** {doctor[1]}")
                            with col2:
                                st.write(f"**Specialization:** {doctor[2]}")
                                st.write(f"**Phone:** {doctor[3]}")
                                
                            st.session_state.doctor_to_remove = doctor
                        else:
                            st.error("❌ No doctor found with this ID.")
                            if 'doctor_to_remove' in st.session_state:
                                del st.session_state.doctor_to_remove
                    else:
                        st.warning("⚠️ Please enter a Doctor ID")
            
            else:  # Search by name
                doc_name = st.text_input("Enter Doctor Name to search", key="remove_doc_name")
                
                if st.button("🔍 Search Doctors", key="search_by_name_for_removal"):
                    if doc_name:
                        # Get all doctors and filter by name (case-insensitive partial match)
                        all_doctors = hms.get_all_doctors()
                        matching_doctors = [doc for doc in all_doctors if doc_name.lower() in doc[1].lower()]
                        
                        if matching_doctors:
                            st.success(f"✅ Found {len(matching_doctors)} doctor(s) matching '{doc_name}'")
                            
                            # Create a dataframe-like display
                            doctor_data = []
                            for doc in matching_doctors:
                                doctor_data.append([doc[0], doc[1], doc[2], doc[3]])
                            
                            display_table(["ID", "Name", "Specialization", "Phone"], doctor_data)
                            
                            # Let user select which doctor to remove
                            st.markdown("---")
                            st.subheader("Select Doctor to Remove")
                            
                            doctor_options = [f"{doc[0]} - Dr. {doc[1]} ({doc[2]})" for doc in matching_doctors]
                            selected_option = st.selectbox("Choose a doctor:", doctor_options, key="select_doctor_to_remove")
                            
                            if selected_option:
                                selected_doc_id = selected_option.split(" - ")[0]
                                # Find the full doctor details
                                for doc in matching_doctors:
                                    if doc[0] == selected_doc_id:
                                        st.session_state.doctor_to_remove = doc
                                        break
                                
                                st.success(f"✅ Selected: Dr. {st.session_state.doctor_to_remove[1]}")
                        else:
                            st.error(f"✗ No doctors found with name containing '{doc_name}'")
                            if 'doctor_to_remove' in st.session_state:
                                del st.session_state.doctor_to_remove
                    else:
                        st.warning("⚠️ Please enter a doctor name to search")
            
            # Show removal confirmation if a doctor is selected
            if 'doctor_to_remove' in st.session_state:
                st.markdown("---")
                st.info("### 👨‍⚕️ Doctor to be Removed")
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**Doctor ID:** {st.session_state.doctor_to_remove[0]}")
                    st.write(f"**Name:** Dr. {st.session_state.doctor_to_remove[1]}")
                with col2:
                    st.write(f"**Specialization:** {st.session_state.doctor_to_remove[2]}")
                    st.write(f"**Phone:** {st.session_state.doctor_to_remove[3]}")
                
                confirm = st.checkbox(f"I confirm that I want to permanently remove Dr. {st.session_state.doctor_to_remove[1]} from the system")
                
                if confirm and st.button("🗑️ Remove Doctor Permanently", type="primary", use_container_width=True):
                    if hms.remove_doctor(st.session_state.doctor_to_remove[0]):
                        st.success(f"✅ Dr. {st.session_state.doctor_to_remove[1]} has been successfully removed from the system.")
                        del st.session_state.doctor_to_remove
                        st.rerun()
                    else:
                        st.error("✗ Failed to remove doctor. Please try again.")
        
        with tab5:
            st.subheader("Scheduled Appointments")
            appointments = hms.get_all_appointments()
            display_table(["Patient ID", "Patient Name", "Doctor Name", "Date", "Time"], appointments)
    
    # Patient Management
    elif page == " 👥 Patient Management":
        st.title("👥 Patient Management")
        
        tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
            "➕ Register Patient", "📋 View Patients", "🔍 Search Patient",
            "📅 Book Appointment", "🏠 Discharge", "💰 Generate Bill"
        ])
        
        with tab1:
            st.subheader("New Patient Registration")
            with st.form("register_patient_form"):
                name = st.text_input("Patient's Full Name")
                col1, col2 = st.columns(2)
                with col1:
                    age = st.text_input("Age")
                    gender = st.selectbox("Gender", ["M", "F", "Other"])
                with col2:
                    phone = st.text_input("Contact Number (10 digits)")
                    email = st.text_input("Email Address")
                address = st.text_area("Residential Address")
                
                submitted = st.form_submit_button("Register Patient")
                
                if submitted:
                    if not all([name, age, phone, address, email]):
                        st.error("❌ All fields are required!")
                    elif not hms.validate_phone(phone):
                        st.error("❌ Invalid phone number! Please enter exactly 10 digits.")
                    else:
                        patient_id = hms.register_patient(name, age, gender, phone, address, email)
                        st.success(f"✅ Patient {name} has been successfully registered with ID: {patient_id}")
        
        with tab2:
            st.subheader("Registered Patients List")
            patients = hms.get_all_patients()
            display_table(["ID", "Name", "Age", "Gender", "Phone", "Status"], patients)
        
        with tab3:
            st.subheader("Search for a Patient")
            search_option = st.radio("Search by:", ["Patient ID", "Patient Name"], horizontal=True)
            
            if search_option == "Patient ID":
                patient_id = st.text_input("Enter Patient ID")
                if st.button("🔍 Search"):
                    patient = hms.search_patient(patient_id)
                    if patient:
                        st.success("✅ Patient Found!")
                        
                        # Create a professional patient view card
                        st.markdown(f"""
                        <div class="patient-card">
                            <div class="patient-header">
                                <h3 style="margin:0;">👤 Patient Details</h3>
                            </div>
                            <div class="info-grid">
                                <div class="info-item">
                                    <div class="info-label">Patient ID</div>
                                    <div class="info-value">{patient[0]}</div>
                                </div>
                                <div class="info-item">
                                    <div class="info-label">Full Name</div>
                                    <div class="info-value">{patient[1]}</div>
                                </div>
                                <div class="info-item">
                                    <div class="info-label">Age</div>
                                    <div class="info-value">{patient[2]}</div>
                                </div>
                                <div class="info-item">
                                    <div class="info-label">Gender</div>
                                    <div class="info-value">{patient[3]}</div>
                                </div>
                                <div class="info-item">
                                    <div class="info-label">Phone</div>
                                    <div class="info-value">{patient[4]}</div>
                                </div>
                                <div class="info-item">
                                    <div class="info-label">Email</div>
                                    <div class="info-value">{patient[6]}</div>
                                </div>
                                <div class="info-item">
                                    <div class="info-label">Status</div>
                                    <div class="info-value">
                                        <span style="color: {'green' if patient[7]=='Admitted' else 'red'}; font-weight: bold;">{patient[7]}</span>
                                    </div>
                                </div>
                                <div class="info-item">
                                    <div class="info-label">Total Charges</div>
                                    <div class="info-value">₹{patient[8]:,.2f}</div>
                                </div>
                            </div>
                            <div style="margin-top: 15px; padding: 10px; background-color: #f8f9fa; border-radius: 5px;">
                                <div class="info-label">Address</div>
                                <div class="info-value">{patient[5]}</div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.error("❌ No patient found with this ID.")
            
            else:  # Search by name
                patient_name = st.text_input("Enter Patient Name (or partial name)")
                if st.button("🔍 Search by Name"):
                    if patient_name:
                        # Get all patients and filter by name (case-insensitive partial match)
                        all_patients = hms.get_all_patients()
                        # all_patients returns (id, name, age, gender, phone, status)
                        matching_patients = [p for p in all_patients if patient_name.lower() in p[1].lower()]
                        
                        if matching_patients:
                            st.success(f"✅ Found {len(matching_patients)} patient(s) matching '{patient_name}'")
                            
                            # Display in a nice table
                            st.markdown("### 📋 Matching Patients")
                            display_table(["ID", "Name", "Age", "Gender", "Phone", "Status"], matching_patients)
                            
                            # Option to view full details of a selected patient
                            if len(matching_patients) > 0:
                                st.markdown("---")
                                st.subheader("🔍 View Complete Patient Details")
                                
                                # Create a selection box with patient names
                                patient_options = [f"{p[0]} - {p[1]} ({p[2]} yrs, {p[3]})" for p in matching_patients]
                                selected_option = st.selectbox("Select a patient to view complete details:", patient_options)
                                
                                if selected_option:
                                    selected_patient_id = selected_option.split(" - ")[0]
                                    
                                    if st.button("📋 Show Full Details", use_container_width=True):
                                        full_patient = hms.search_patient(selected_patient_id)
                                        if full_patient:
                                            # Create a professional patient view card
                                            st.markdown(f"""
                                            <div class="patient-card">
                                                <div class="patient-header">
                                                    <h3 style="margin:0;">👤 Complete Patient Details</h3>
                                                </div>
                                                <div class="info-grid">
                                                    <div class="info-item">
                                                        <div class="info-label">Patient ID</div>
                                                        <div class="info-value">{full_patient[0]}</div>
                                                    </div>
                                                    <div class="info-item">
                                                        <div class="info-label">Full Name</div>
                                                        <div class="info-value">{full_patient[1]}</div>
                                                    </div>
                                                    <div class="info-item">
                                                        <div class="info-label">Age</div>
                                                        <div class="info-value">{full_patient[2]}</div>
                                                    </div>
                                                    <div class="info-item">
                                                        <div class="info-label">Gender</div>
                                                        <div class="info-value">{full_patient[3]}</div>
                                                    </div>
                                                    <div class="info-item">
                                                        <div class="info-label">Phone</div>
                                                        <div class="info-value">{full_patient[4]}</div>
                                                    </div>
                                                    <div class="info-item">
                                                        <div class="info-label">Email</div>
                                                        <div class="info-value">{full_patient[6]}</div>
                                                    </div>
                                                    <div class="info-item">
                                                        <div class="info-label">Status</div>
                                                        <div class="info-value">
                                                            <span style="color: {'green' if full_patient[7]=='Admitted' else 'red'}; font-weight: bold;">{full_patient[7]}</span>
                                                        </div>
                                                    </div>
                                                    <div class="info-item">
                                                        <div class="info-label">Total Charges</div>
                                                        <div class="info-value">₹{full_patient[8]:,.2f}</div>
                                                    </div>
                                                </div>
                                                <div style="margin-top: 15px; padding: 10px; background-color: #f8f9fa; border-radius: 5px;">
                                                    <div class="info-label">Address</div>
                                                    <div class="info-value">{full_patient[5]}</div>
                                                </div>
                                            </div>
                                            """, unsafe_allow_html=True)
                        else:
                            st.error(f"✗ No patients found with name containing '{patient_name}'")
                    else:
                        st.warning("⚠️ Please enter a patient name to search")
        
        with tab4:
            st.subheader("Schedule New Appointment")
            with st.form("book_appointment_form"):
                patient_id = st.text_input("Patient ID")
                
                doctors = hms.get_all_doctors()
                if doctors:
                    doctor_options = [f"{d[0]} - Dr. {d[1]} ({d[2]})" for d in doctors]
                    selected_doctor = st.selectbox("Select Doctor", doctor_options)
                else:
                    st.warning("⚠️ No doctors available. Please add doctors first.")
                    selected_doctor = None
                
                col1, col2 = st.columns(2)
                with col1:
                    date = st.date_input("Appointment Date")
                with col2:
                    time = st.time_input("Appointment Time")
                
                submitted = st.form_submit_button("📅 Book Appointment")
                
                if submitted:
                    if not selected_doctor:
                        st.error("❌ No doctors available!")
                    else:
                        doc_id = selected_doctor.split(" - ")[0]
                        date_str = date.strftime("%d-%m-%Y")
                        time_str = time.strftime("%H:%M")
                        
                        if hms.book_appointment(patient_id, doc_id, date_str, time_str):
                            st.success("✅ Appointment has been scheduled successfully!")
                        else:
                            st.error("❌ Patient or Doctor not found!")
        
        with tab5:
            st.subheader("🏠 Discharge Patient")
            patient_id = st.text_input("Enter Patient ID to discharge")
            if st.button("🏠 Discharge Patient"):
                patient = hms.search_patient(patient_id)
                if patient:
                    hms.discharge_patient(patient_id)
                    st.success("✅ Patient discharged successfully!")
                else:
                    st.error("❌ Patient not found!")
        
        with tab6:
            st.subheader("💰 Generate Patient Bill")
            patient_id = st.text_input("Enter Patient ID for billing", key="bill_patient_id")
            
            if patient_id:
                patient = hms.search_patient(patient_id)
                if patient:
                    st.success(f"✅ Patient Found: {patient[1]}")
                    
                    # Patient Information Section
                    with st.expander("📋 Patient Information", expanded=True):
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.write(f"**Patient ID:** {patient[0]}")
                            st.write(f"**Name:** {patient[1]}")
                        with col2:
                            st.write(f"**Age/Gender:** {patient[2]}/{patient[3]}")
                            st.write(f"**Phone:** {patient[4]}")
                        with col3:
                            st.write(f"**Email:** {patient[6]}")
                            st.write(f"**Status:** {patient[7]}")
                    
                    st.markdown("---")
                    st.markdown("### ➕ Add Services & Charges")
                    
                    # Create two columns for better organization
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("**👨‍⚕️ Medical Services**")
                        consultation = st.checkbox("Doctor Consultation (₹500)", key="consult")
                        specialist_consult = st.checkbox("Specialist Consultation (₹1000)", key="specialist")
                        emergency = st.checkbox("Emergency Services (₹2000)", key="emergency")
                        ambulance = st.checkbox("Ambulance Service (₹1500)", key="ambulance")
                        
                        st.markdown("**💊 Pharmacy & Supplies**")
                        medicines = st.number_input("Medicines (₹)", min_value=0.0, step=100.0, key="medicines")
                        medical_supplies = st.number_input("Medical Supplies (₹)", min_value=0.0, step=100.0, key="supplies")
                        
                    with col2:
                        st.markdown("**🔬 Diagnostics**")
                        lab_tests = st.number_input("Laboratory Tests (₹)", min_value=0.0, step=100.0, key="lab")
                        radiology = st.number_input("Radiology/X-Ray (₹)", min_value=0.0, step=100.0, key="xray")
                        mri_ct = st.number_input("MRI/CT Scan (₹)", min_value=0.0, step=1000.0, key="scan")
                        
                        st.markdown("**🏥 Facility Charges**")
                        room_days = st.number_input("Room Charges (days)", min_value=0, step=1, key="room")
                        icu_days = st.number_input("ICU Charges (days)", min_value=0, step=1, key="icu")
                        surgery = st.number_input("Surgical Procedures (₹)", min_value=0.0, step=1000.0, key="surgery")
                    
                    # Additional charges
                    st.markdown("**📝 Other Charges**")
                    col3, col4 = st.columns(2)
                    with col3:
                        nursing = st.number_input("Nursing Care (₹)", min_value=0.0, step=100.0, key="nursing")
                        physiotherapy = st.number_input("Physiotherapy (₹)", min_value=0.0, step=100.0, key="physio")
                    with col4:
                        dietary = st.number_input("Dietary Services (₹)", min_value=0.0, step=100.0, key="diet")
                        miscellaneous = st.number_input("Miscellaneous (₹)", min_value=0.0, step=100.0, key="misc")
                    
                    # Discount and payment details
                    st.markdown("---")
                    col5, col6 = st.columns(2)
                    with col5:
                        discount = st.number_input("Discount (%)", min_value=0.0, max_value=100.0, step=1.0, key="discount")
                    with col6:
                        advance_paid = st.number_input("Advance Paid (₹)", min_value=0.0, step=500.0, key="advance")
                    
                    # Collect services
                    services = []
                    
                    # Medical Services
                    if consultation:
                        services.append(("Doctor Consultation", 500))
                    if specialist_consult:
                        services.append(("Specialist Consultation", 1000))
                    if emergency:
                        services.append(("Emergency Services", 2000))
                    if ambulance:
                        services.append(("Ambulance Service", 1500))
                    
                    # Pharmacy
                    if medicines > 0:
                        services.append(("Medicines", medicines))
                    if medical_supplies > 0:
                        services.append(("Medical Supplies", medical_supplies))
                    
                    # Diagnostics
                    if lab_tests > 0:
                        services.append(("Laboratory Tests", lab_tests))
                    if radiology > 0:
                        services.append(("Radiology/X-Ray", radiology))
                    if mri_ct > 0:
                        services.append(("MRI/CT Scan", mri_ct))
                    
                    # Facility
                    if room_days > 0:
                        services.append((f"Room Charges ({room_days} days)", room_days * 1500))
                    if icu_days > 0:
                        services.append((f"ICU Charges ({icu_days} days)", icu_days * 5000))
                    if surgery > 0:
                        services.append(("Surgical Procedures", surgery))
                    
                    # Other
                    if nursing > 0:
                        services.append(("Nursing Care", nursing))
                    if physiotherapy > 0:
                        services.append(("Physiotherapy", physiotherapy))
                    if dietary > 0:
                        services.append(("Dietary Services", dietary))
                    if miscellaneous > 0:
                        services.append(("Miscellaneous", miscellaneous))
                    
                    if services:
                        if st.button("💰 Generate Professional Bill", type="primary", use_container_width=True):
                            # Calculate totals
                            subtotal = sum(amount for _, amount in services)
                            discount_amount = (subtotal * discount) / 100
                            taxable_amount = subtotal - discount_amount
                            tax = taxable_amount * 0.05  # 5% GST
                            total = taxable_amount + tax
                            balance_due = total - advance_paid
                            
                            # Generate bill number and date
                            bill_no = f"LJH{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"
                            bill_date = datetime.datetime.now().strftime("%d-%m-%Y %I:%M %p")
                            due_date = (datetime.datetime.now() + datetime.timedelta(days=15)).strftime("%d-%m-%Y")
                            
                            # Update patient charges
                            hms.update_patient_charges(patient_id, total)
                            
                            # Store bill in session state
                            st.session_state.bill_generated = True
                            st.session_state.current_bill = {
                                'bill_no': bill_no,
                                'bill_date': bill_date,
                                'due_date': due_date,
                                'patient_id': patient[0],
                                'patient_name': patient[1],
                                'patient_email': patient[6],
                                'patient_phone': patient[4],
                                'patient_address': patient[5],
                                'services': services,
                                'subtotal': subtotal,
                                'discount': discount,
                                'discount_amount': discount_amount,
                                'taxable_amount': taxable_amount,
                                'tax': tax,
                                'total': total,
                                'advance_paid': advance_paid,
                                'balance_due': balance_due
                            }
                            st.rerun()
                    
                    # Display generated bill with professional format
                    if st.session_state.bill_generated and st.session_state.current_bill:
                        bill = st.session_state.current_bill
                        
                        # Professional Bill Format - REAL BILL STYLE
                        st.markdown('<div class="bill-container">', unsafe_allow_html=True)
                        
                        # Header with Logo and Title
                        st.markdown("""
                        <div class="bill-header">
                            <h1>🏥 LJ HOSPITAL & MEDICAL CENTER</h1>
                            <h3>Complete Healthcare Solutions</h3>
                            <p>123 Healthcare Avenue, Medical District, City - 400001</p>
                            <p>📞 +91-9924822196 | 📧 accounts@ljhospital.com | 🌐 www.ljhospital.com</p>
                            <p>GSTIN: 27ABCDE1234F1Z5 | CIN: U85110MH2020PTC123456</p>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Bill Title with decorative line
                        st.markdown("""
                        <div style="text-align: center; margin: 20px 0;">
                            <h2 style="color: #1f77b4; border-bottom: 2px solid #1f77b4; display: inline-block; padding-bottom: 10px;">TAX INVOICE / BILL</h2>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Bill Information Box
                        st.markdown(f"""
                        <div class="bill-info">
                            <table style="width: 100%;">
                                <tr>
                                    <td><strong>Bill No:</strong> {bill['bill_no']}</td>
                                    <td><strong>Bill Date:</strong> {bill['bill_date']}</td>
                                    <td><strong>Due Date:</strong> {bill['due_date']}</td>
                                </tr>
                                <tr>
                                    <td><strong>Payment Terms:</strong> Due on receipt</td>
                                    <td><strong>Mode:</strong> Cash/Card/UPI</td>
                                    <td><strong>Reference:</strong> {bill['patient_id']}</td>
                                </tr>
                            </table>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Patient Details in two columns
                        st.markdown("""
                        <div style="background-color: #f1f1f1; padding: 15px; border-radius: 5px; margin: 20px 0;">
                            <h4 style="color: #1f77b4; margin-top: 0;">👤 PATIENT DETAILS</h4>
                        """, unsafe_allow_html=True)
                        
                        col_p1, col_p2 = st.columns(2)
                        with col_p1:
                            st.markdown(f"""
                            **Patient Name:** {bill['patient_name']}<br>
                            **Patient ID:** {bill['patient_id']}<br>
                            **Phone:** {bill['patient_phone']}
                            """, unsafe_allow_html=True)
                        with col_p2:
                            st.markdown(f"""
                            **Email:** {bill['patient_email']}<br>
                            **Address:** {bill['patient_address'][:50]}...
                            """, unsafe_allow_html=True)
                        
                        st.markdown("</div>", unsafe_allow_html=True)
                        
                        # Services Table - FIXED VERSION
                        st.markdown('<h4 style="color: #1f77b4;">📋 SERVICE DETAILS</h4>', unsafe_allow_html=True)
                        
                        # Create professional HTML table for services - FIXED FORMATTING
                        service_table = "<table class='bill-table'><thead><tr>"
                        service_table += "<th style='width: 10%;'>S.No.</th>"
                        service_table += "<th style='width: 60%;'>Description</th>"
                        service_table += "<th style='width: 30%; text-align: right;'>Amount (₹)</th>"
                        service_table += "</tr></thead><tbody>"
                        
                        for idx, (service, amount) in enumerate(bill['services'], 1):
                            service_table += "<tr>"
                            service_table += f"<td style='text-align: center;'>{idx}</td>"
                            service_table += f"<td>{service}</td>"
                            service_table += f"<td style='text-align: right;'>₹{amount:,.2f}</td>"
                            service_table += "</tr>"
                        
                        service_table += "</tbody></table>"
                        
                        st.markdown(service_table, unsafe_allow_html=True)
                        
                        # Summary Box
                        st.markdown("""
                        <div class="summary-box">
                            <h4 style="color: #1f77b4; margin-top: 0;">💰 CHARGE SUMMARY</h4>
                        """, unsafe_allow_html=True)
                        
                        col_s1, col_s2, col_s3 = st.columns([1, 1, 1])
                        
                        with col_s1:
                            st.markdown(f"""
                            **Subtotal:** ₹{bill['subtotal']:,.2f}<br>
                            **Discount ({bill['discount']:.1f}%):** <span style="color: red;">-₹{bill['discount_amount']:,.2f}</span><br>
                            **Taxable Amount:** ₹{bill['taxable_amount']:,.2f}
                            """, unsafe_allow_html=True)
                        
                        with col_s2:
                            st.markdown(f"""
                            **CGST (2.5%):** ₹{bill['tax']/2:,.2f}<br>
                            **SGST (2.5%):** ₹{bill['tax']/2:,.2f}<br>
                            **Total Tax:** ₹{bill['tax']:,.2f}
                            """, unsafe_allow_html=True)
                        
                        with col_s3:
                            st.markdown(f"""
                            <div style="background-color: #1f77b4; color: white; padding: 10px; border-radius: 5px;">
                                <strong>Total Amount:</strong> ₹{bill['total']:,.2f}<br>
                                <strong>Advance Paid:</strong> ₹{bill['advance_paid']:,.2f}<br>
                                <strong>Balance Due:</strong> <span style="font-size: 20px;">₹{bill['balance_due']:,.2f}</span>
                            </div>
                            """, unsafe_allow_html=True)
                        
                        st.markdown("</div>", unsafe_allow_html=True)
                        
                        # Amount in words with professional styling
                        st.markdown(f"""
                        <div class="amount-words">
                            <strong>Amount in Words:</strong> {number_to_words(bill['total'])}
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Payment Options (QR Code/Scan Pay removed, other options kept)
                        st.markdown(f"""
                        <div class="payment-info">
                            <h4 style="color: #1f77b4; margin-top: 0;">💳 Payment Options</h4>
                            <div>
                                <p><strong>UPI ID:</strong> ljhospital@okhdfcbank</p>
                                <p><strong>Bank:</strong> HDFC Bank, Medical Branch</p>
                                <p><strong>Account:</strong> 50100234567890 | <strong>IFSC:</strong> HDFC0001234</p>
                                <p><strong>Cash/Card payments accepted at counter</strong></p>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Terms and Conditions
                        st.markdown("""
                        <div class="terms-box">
                            <h4 style="color: #856404; margin-top: 0;">📝 TERMS & CONDITIONS</h4>
                            <ol style="margin-bottom: 0;">
                                <li>This is a computer generated invoice - valid without signature</li>
                                <li>Payment is due within 15 days of bill date</li>
                                <li>Late payment may attract interest @ 18% per annum</li>
                                <li>For any queries, contact billing department at accounts@ljhospital.com</li>
                                <li>Insurance claims to be submitted within 7 days of discharge</li>
                                <li>This bill includes all applicable taxes as per GST rules</li>
                            </ol>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Footer
                        st.markdown("""
                        <div class="footer">
                            <p><strong>Thank you for choosing LJ Hospital. Wishing you good health!</strong> 🌟</p>
                            <p style="font-size: 12px; color: #999;">This is a system generated bill - no signature required</p>
                            <p style="font-size: 12px; color: #999;">Bill generated on: """ + datetime.datetime.now().strftime("%d-%m-%Y %I:%M %p") + """</p>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        st.markdown('</div>', unsafe_allow_html=True)  # Close bill-container
                        
                        # Action Buttons
                        st.markdown("---")
                        col_b1, col_b2, col_b3, col_b4 = st.columns(4)
                        
                        with col_b1:
                            if st.button("📧 Send Bill via Email", key="send_email_btn2", use_container_width=True):
                                # Send the beautifully formatted HTML bill
                                if hms.send_bill_email(bill['patient_email'], bill, bill['patient_name'], bill['total']):
                                    st.success(f"✅ Beautifully formatted bill sent to {bill['patient_email']}")
                                    st.info("📧 The bill has been sent as an HTML email that looks exactly like the bill shown above!")
                                else:
                                    st.error("❌ Failed to send email.")
                        
                        with col_b2:
                            if st.button("🖨️ Print Bill", key="print_bill", use_container_width=True):
                                st.info("💡 Use browser print (Ctrl+P) to print this bill")
                        
                        with col_b3:
                            if st.button("💾 Download PDF", key="download_pdf", use_container_width=True):
                                st.info("💡 Coming soon: PDF download feature")
                        
                        with col_b4:
                            if st.button("🔄 New Bill", key="reset_bill_btn2", use_container_width=True):
                                st.session_state.bill_generated = False
                                st.session_state.current_bill = None
                                st.rerun()
                else:
                    st.error("❌ Patient not found! Please enter a valid Patient ID.")
    
    # Reports
    elif page == " 📊 Reports":
        st.title("📊 System Reports")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("👨‍⚕️ Total Doctors", len(hms.get_all_doctors()))
        with col2:
            admitted = len([p for p in hms.get_all_patients() if p[5] == 'Admitted'])
            st.metric("🏥 Admitted Patients", admitted)
        with col3:
            st.metric("📅 Total Appointments", len(hms.get_all_appointments()))
        
        st.markdown("---")
        
        # Recent Appointments
        st.subheader("📋 Recent Appointments")
        appointments = hms.get_all_appointments()
        if appointments:
            recent_appointments = appointments[-10:] if len(appointments) > 10 else appointments
            display_table(["Patient ID", "Patient Name", "Doctor Name", "Date", "Time"], recent_appointments)
        else:
            st.info("📝 No appointments scheduled yet.")
    
    # Settings
    elif page == " ⚙️ Settings":
        st.title("⚙️ System Settings") 
        st.subheader("💾 Database Information")
        st.write(f"**Database File:** `hospital_management.db`")
        st.write(f"**👨‍⚕️ Total Doctors:** {len(hms.get_all_doctors())}")
        st.write(f"**👥 Total Patients:** {len(hms.get_all_patients())}")
        st.write(f"**📅 Total Appointments:** {len(hms.get_all_appointments())}")
