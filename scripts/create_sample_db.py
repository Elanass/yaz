#!/usr/bin/env python3
"""
Direct database sample data loader for Surgify Platform
Loads data directly into SQLite database
"""

import sys
import os
from datetime import datetime, timedelta
import random
import sqlite3
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

def create_sample_data():
    """Create sample data directly in the database"""
    
    # Database path
    db_path = Path(__file__).parent.parent / "data" / "database" / "surgify.db"
    db_path.parent.mkdir(parents=True, exist_ok=True)
    
    print(f"🗄️  Connecting to database: {db_path}")
    
    try:
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        # Create tables if they don't exist
        print("📋 Creating database tables...")
        
        # Users table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username VARCHAR(50) UNIQUE NOT NULL,
                email VARCHAR(100) UNIQUE NOT NULL,
                full_name VARCHAR(100) NOT NULL,
                role VARCHAR(20) DEFAULT 'user',
                department VARCHAR(50),
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                is_active BOOLEAN DEFAULT 1
            )
        """)
        
        # Patients table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS patients (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_id VARCHAR(50) UNIQUE NOT NULL,
                age INTEGER,
                gender VARCHAR(10),
                bmi FLOAT,
                medical_history TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Cases table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS cases (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                case_number VARCHAR(50) UNIQUE NOT NULL,
                patient_id VARCHAR(50) NOT NULL,
                procedure_type VARCHAR(100) NOT NULL,
                diagnosis TEXT,
                status VARCHAR(20) DEFAULT 'planned',
                priority VARCHAR(20) DEFAULT 'medium',
                surgeon_id VARCHAR(50),
                scheduled_date DATETIME,
                actual_start DATETIME,
                actual_end DATETIME,
                risk_score FLOAT,
                notes TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Clear existing data
        print("🧹 Clearing existing data...")
        cursor.execute("DELETE FROM cases")
        cursor.execute("DELETE FROM patients") 
        cursor.execute("DELETE FROM users")
        
        # Insert sample users
        print("👥 Creating sample users...")
        users = [
            ("sarah.johnson", "sarah.johnson@surgify.com", "Dr. Sarah Johnson", "surgeon", "general_surgery"),
            ("michael.chen", "michael.chen@surgify.com", "Dr. Michael Chen", "surgeon", "cardiac_surgery"),
            ("emily.rodriguez", "emily.rodriguez@surgify.com", "Dr. Emily Rodriguez", "surgeon", "orthopedic_surgery"),
            ("david.kim", "david.kim@surgify.com", "Dr. David Kim", "surgeon", "neurosurgery"),
            ("lisa.thompson", "lisa.thompson@surgify.com", "Dr. Lisa Thompson", "surgeon", "general_surgery"),
            ("admin", "admin@surgify.com", "System Administrator", "admin", "administration"),
            ("nurse.jane", "jane.doe@surgify.com", "Jane Doe", "nurse", "general_surgery"),
            ("analyst", "analyst@surgify.com", "Data Analyst", "analyst", "analytics")
        ]
        
        cursor.executemany("""
            INSERT INTO users (username, email, full_name, role, department)
            VALUES (?, ?, ?, ?, ?)
        """, users)
        
        # Insert sample patients
        print("🏥 Creating sample patients...")
        patients = []
        for i in range(50):
            patients.append((
                f"PAT-{i+1:03d}",
                random.randint(25, 85),
                random.choice(["male", "female"]),
                round(random.uniform(18.5, 35.0), 1),
                random.choice([
                    "diabetes_type2",
                    "hypertension", 
                    "diabetes_type2,hypertension",
                    "none",
                    "cardiovascular_disease",
                    "diabetes_type2,cardiovascular_disease"
                ])
            ))
        
        cursor.executemany("""
            INSERT INTO patients (patient_id, age, gender, bmi, medical_history)
            VALUES (?, ?, ?, ?, ?)
        """, patients)
        
        # Insert sample cases
        print("📋 Creating sample cases...")
        procedures = [
            "Laparoscopic Cholecystectomy",
            "Appendectomy",
            "Hernia Repair", 
            "Gastric Bypass",
            "Colon Resection",
            "Thyroidectomy",
            "Mastectomy",
            "Knee Replacement",
            "Hip Replacement",
            "Cardiac Bypass"
        ]
        
        statuses = ["planned", "in_progress", "completed", "cancelled"]
        priorities = ["low", "medium", "high", "urgent"]
        surgeon_usernames = ["sarah.johnson", "michael.chen", "emily.rodriguez", "david.kim", "lisa.thompson"]
        
        cases = []
        for i in range(75):
            patient_id = f"PAT-{random.randint(1, 50):03d}"
            procedure = random.choice(procedures)
            scheduled_date = datetime.now() + timedelta(days=random.randint(-30, 60))
            
            cases.append((
                f"CASE-{i+1:04d}",
                patient_id,
                procedure,
                f"Diagnosis for {procedure}",
                random.choice(statuses),
                random.choice(priorities),
                random.choice(surgeon_usernames),
                scheduled_date.isoformat(),
                round(random.uniform(0.1, 0.9), 2),
                f"Sample case for {procedure} - Patient {patient_id}"
            ))
        
        cursor.executemany("""
            INSERT INTO cases (case_number, patient_id, procedure_type, diagnosis, status, priority, 
                             surgeon_id, scheduled_date, risk_score, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, cases)
        
        # Commit changes
        conn.commit()
        
        # Display summary
        print("\n✅ Sample data created successfully!")
        print(f"   👥 {len(users)} users")
        print(f"   🏥 {len(patients)} patients") 
        print(f"   📋 {len(cases)} cases")
        
        # Show some stats
        cursor.execute("SELECT COUNT(*) FROM users")
        user_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM patients")
        patient_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM cases")
        case_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT procedure_type, COUNT(*) FROM cases GROUP BY procedure_type ORDER BY COUNT(*) DESC LIMIT 5")
        top_procedures = cursor.fetchall()
        
        print(f"\n📊 Database Summary:")
        print(f"   📈 Total Users: {user_count}")
        print(f"   📈 Total Patients: {patient_count}")
        print(f"   📈 Total Cases: {case_count}")
        print(f"\n🏆 Top Procedures:")
        for proc, count in top_procedures:
            print(f"   • {proc}: {count} cases")
        
        print(f"\n🌐 You can now access:")
        print(f"   📱 Web UI: http://localhost:8000")
        print(f"   📚 API Docs: http://localhost:8000/docs")
        print(f"   📈 Dashboard: http://localhost:8000/dashboard")
        
    except Exception as e:
        print(f"❌ Error creating sample data: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    create_sample_data()
