#!/usr/bin/env python3
"""
Sample data loader for Surgify Platform
Creates realistic sample data for development and testing
"""

import json
import asyncio
from datetime import datetime, timedelta
from typing import List, Dict, Any
import httpx
import random

BASE_URL = "http://localhost:8000"

# Sample data generators
def generate_patients(count: int = 50) -> List[Dict[str, Any]]:
    """Generate sample patient data"""
    patients = []
    for i in range(count):
        patients.append({
            "patient_id": f"PAT-{i+1:03d}",
            "age": random.randint(25, 85),
            "gender": random.choice(["male", "female"]),
            "bmi": round(random.uniform(18.5, 35.0), 1),
            "medical_history": random.choice([
                "diabetes_type2",
                "hypertension",
                "diabetes_type2,hypertension",
                "none",
                "cardiovascular_disease",
                "diabetes_type2,cardiovascular_disease"
            ])
        })
    return patients

def generate_users(count: int = 10) -> List[Dict[str, Any]]:
    """Generate sample user data"""
    users = []
    surgeon_names = [
        "Dr. Sarah Johnson", "Dr. Michael Chen", "Dr. Emily Rodriguez",
        "Dr. David Kim", "Dr. Lisa Thompson", "Dr. James Wilson",
        "Dr. Maria Garcia", "Dr. Robert Davis", "Dr. Jennifer Lee", "Dr. Christopher Brown"
    ]
    
    for i, name in enumerate(surgeon_names[:count]):
        users.append({
            "username": name.lower().replace(" ", ".").replace("dr.", ""),
            "email": f"{name.lower().replace(' ', '.').replace('dr.', '')}@surgify.com",
            "full_name": name,
            "role": "surgeon" if i < count - 2 else "nurse",
            "department": random.choice(["general_surgery", "cardiac_surgery", "orthopedic_surgery", "neurosurgery"])
        })
    
    return users

def generate_cases(patients: List[Dict], users: List[Dict], count: int = 100) -> List[Dict[str, Any]]:
    """Generate sample case data"""
    cases = []
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
    
    for i in range(count):
        patient = random.choice(patients)
        surgeon = random.choice([u for u in users if u["role"] == "surgeon"])
        procedure = random.choice(procedures)
        
        scheduled_date = datetime.now() + timedelta(days=random.randint(-30, 60))
        
        cases.append({
            "case_number": f"CASE-{i+1:04d}",
            "patient_id": patient["patient_id"],
            "procedure_type": procedure,
            "diagnosis": f"Diagnosis for {procedure}",
            "status": random.choice(statuses),
            "priority": random.choice(priorities),
            "surgeon_id": surgeon["username"],
            "scheduled_date": scheduled_date.isoformat(),
            "risk_score": round(random.uniform(0.1, 0.9), 2),
            "notes": f"Sample case for {procedure} - Patient {patient['patient_id']}"
        })
    
    return cases

async def load_sample_data():
    """Load sample data into the system"""
    async with httpx.AsyncClient(timeout=30.0) as client:
        print("🚀 Loading sample data for Surgify...")
        
        # Generate sample data
        print("📊 Generating sample data...")
        patients = generate_patients(50)
        users = generate_users(8)
        cases = generate_cases(patients, users, 75)
        
        try:
            # Load users first
            print("👥 Loading users...")
            for user in users:
                try:
                    response = await client.post(f"{BASE_URL}/api/v1/users/", json=user)
                    if response.status_code in [200, 201]:
                        print(f"  ✅ User: {user['full_name']}")
                    else:
                        print(f"  ⚠️  User {user['full_name']}: {response.status_code}")
                except Exception as e:
                    print(f"  ❌ User {user['full_name']}: {e}")
            
            # Load patients
            print("🏥 Loading patients...")
            for patient in patients:
                try:
                    response = await client.post(f"{BASE_URL}/api/v1/patients/", json=patient)
                    if response.status_code in [200, 201]:
                        print(f"  ✅ Patient: {patient['patient_id']}")
                    else:
                        print(f"  ⚠️  Patient {patient['patient_id']}: {response.status_code}")
                except Exception as e:
                    print(f"  ❌ Patient {patient['patient_id']}: {e}")
            
            # Load cases
            print("📋 Loading cases...")
            for case in cases:
                try:
                    response = await client.post(f"{BASE_URL}/api/v1/cases/", json=case)
                    if response.status_code in [200, 201]:
                        print(f"  ✅ Case: {case['case_number']} - {case['procedure_type']}")
                    else:
                        print(f"  ⚠️  Case {case['case_number']}: {response.status_code} - {response.text[:100]}")
                except Exception as e:
                    print(f"  ❌ Case {case['case_number']}: {e}")
            
            print("\n🎉 Sample data loading completed!")
            print(f"   📊 {len(users)} users, {len(patients)} patients, {len(cases)} cases")
            print("\n🌐 You can now access:")
            print(f"   📱 Web UI: {BASE_URL}")
            print(f"   📚 API Docs: {BASE_URL}/docs")
            print(f"   📈 Dashboard: {BASE_URL}/dashboard")
            
        except Exception as e:
            print(f"❌ Error loading sample data: {e}")

if __name__ == "__main__":
    asyncio.run(load_sample_data())
