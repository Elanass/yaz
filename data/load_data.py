"""
Data loader for Surgify platform using existing test samples
"""

import json
import os
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path


def initialize_sample_data():
    """Initialize database with sample data from test_samples"""

    # Create database directory if it doesn't exist
    db_dir = Path("/workspaces/yaz/data/database")
    db_dir.mkdir(parents=True, exist_ok=True)

    # Database path
    db_path = db_dir / "surgify.db"

    # Connect to SQLite database
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()

    try:
        # Create tables
        create_tables(cursor)

        # Load test samples
        test_samples_dir = Path("/workspaces/yaz/data/test_samples")
        if test_samples_dir.exists():
            load_test_samples(cursor, test_samples_dir)

        # Commit changes
        conn.commit()
        print("✅ Sample data initialized successfully!")

    except Exception as e:
        print(f"❌ Error initializing sample data: {e}")
        conn.rollback()
    finally:
        conn.close()


def create_tables(cursor):
    """Create database tables"""

    # Users table
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            hashed_password TEXT NOT NULL,
            full_name TEXT,
            role TEXT DEFAULT 'surgeon',
            is_active BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """
    )

    # Patients table
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS patients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id TEXT UNIQUE NOT NULL,
            age INTEGER,
            gender TEXT,
            bmi REAL,
            medical_history TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """
    )

    # Cases table
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS cases (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            case_number TEXT UNIQUE NOT NULL,
            patient_id INTEGER REFERENCES patients(id),
            surgeon_id INTEGER REFERENCES users(id),
            procedure_type TEXT,
            diagnosis TEXT,
            status TEXT DEFAULT 'planned',
            scheduled_date TIMESTAMP,
            actual_start TIMESTAMP,
            actual_end TIMESTAMP,
            risk_score REAL,
            recommendations TEXT,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """
    )

    # Protocols table
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS protocols (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            version TEXT,
            procedure_type TEXT,
            steps TEXT,
            guidelines TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """
    )


def load_test_samples(cursor, test_samples_dir):
    """Load data from test samples"""

    # Sample users
    users = [
        (
            "dr_smith",
            "smith@hospital.com",
            "$2b$12$example_hash",
            "Dr. John Smith",
            "surgeon",
        ),
        (
            "dr_johnson",
            "johnson@hospital.com",
            "$2b$12$example_hash",
            "Dr. Sarah Johnson",
            "surgeon",
        ),
        (
            "dr_wilson",
            "wilson@hospital.com",
            "$2b$12$example_hash",
            "Dr. Michael Wilson",
            "surgeon",
        ),
    ]

    cursor.executemany(
        """
        INSERT OR IGNORE INTO users (username, email, hashed_password, full_name, role)
        VALUES (?, ?, ?, ?, ?)
    """,
        users,
    )

    # Sample patients
    patients = [
        ("P001", 65, "Male", 28.5, '{"conditions": ["diabetes", "hypertension"]}'),
        ("P002", 58, "Female", 24.2, '{"conditions": ["gastric_ulcer"]}'),
        ("P003", 72, "Male", 26.8, '{"conditions": ["gastric_cancer"]}'),
        ("P004", 45, "Female", 22.1, '{"conditions": ["GERD"]}'),
        ("P005", 63, "Male", 29.3, '{"conditions": ["gastric_polyps"]}'),
    ]

    cursor.executemany(
        """
        INSERT OR IGNORE INTO patients (patient_id, age, gender, bmi, medical_history)
        VALUES (?, ?, ?, ?, ?)
    """,
        patients,
    )

    # Sample cases
    now = datetime.now()
    cases = [
        (
            "SURG-001",
            1,
            1,
            "gastric_resection",
            "Gastric adenocarcinoma",
            "planned",
            now + timedelta(days=3),
            None,
            None,
            0.4,
            '["Consider neoadjuvant therapy", "Ensure nutritional support"]',
            "",
        ),
        (
            "SURG-002",
            2,
            2,
            "laparoscopic",
            "Gastric ulcer perforation",
            "in_progress",
            now,
            now - timedelta(hours=1),
            None,
            0.2,
            '["Monitor vital signs", "Prepare for conversion if needed"]',
            "",
        ),
        (
            "SURG-003",
            3,
            1,
            "open_surgery",
            "Advanced gastric cancer",
            "completed",
            now - timedelta(days=1),
            now - timedelta(days=1, hours=2),
            now - timedelta(days=1),
            0.6,
            '["Adjuvant chemotherapy", "Regular follow-up"]',
            "",
        ),
        (
            "SURG-004",
            4,
            2,
            "endoscopic",
            "Gastric polyp removal",
            "planned",
            now + timedelta(days=1),
            None,
            None,
            0.1,
            '["Standard endoscopic procedure", "Biopsy recommended"]',
            "",
        ),
        (
            "SURG-005",
            5,
            3,
            "gastric_bypass",
            "Obesity with gastric complications",
            "scheduled",
            now + timedelta(days=7),
            None,
            None,
            0.3,
            '["Pre-operative weight management", "Nutritional counseling"]',
            "",
        ),
    ]

    cursor.executemany(
        """
        INSERT OR IGNORE INTO cases (
            case_number, patient_id, surgeon_id, procedure_type, diagnosis, status,
            scheduled_date, actual_start, actual_end, risk_score, recommendations, notes
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """,
        cases,
    )

    # Sample protocols
    protocols = [
        (
            "Standard Gastric Resection",
            "1.0",
            "gastric_resection",
            '["Patient preparation", "Anesthesia induction", "Surgical incision", "Gastric mobilization", "Resection", "Reconstruction", "Closure"]',
            "Standard protocol for gastric resection procedures",
        ),
        (
            "Laparoscopic Surgery Protocol",
            "1.0",
            "laparoscopic",
            '["Setup laparoscopic equipment", "Patient positioning", "Trocar placement", "Insufflation", "Procedure", "Inspection", "Closure"]',
            "Minimally invasive laparoscopic procedures",
        ),
        (
            "Emergency Surgery Protocol",
            "1.0",
            "emergency",
            '["Rapid assessment", "Stabilization", "Immediate intervention", "Damage control", "ICU transfer"]',
            "Emergency surgical intervention protocol",
        ),
    ]

    cursor.executemany(
        """
        INSERT OR IGNORE INTO protocols (name, version, procedure_type, steps, guidelines)
        VALUES (?, ?, ?, ?, ?)
    """,
        protocols,
    )


if __name__ == "__main__":
    initialize_sample_data()
