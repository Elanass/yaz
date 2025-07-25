#!/usr/bin/env python3
"""
Test script for the Gastric ADCI Platform
Tests both backend and frontend functionality
"""

import asyncio
import httpx
import json
import sys
import os
from pathlib import Path
import pytest

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Backend API base URL
BACKEND_URL = "http://localhost:8000"
FRONTEND_URL = "http://localhost:8001"

class ADCITestSuite:
    """Test suite for ADCI platform"""
    
    def __init__(self):
        self.client = httpx.AsyncClient()
        self.auth_token = None
        self.test_user_id = None
        self.test_patient_id = None
        self.test_protocol_id = None
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()
    
    async def test_backend_health(self):
        """Test backend health endpoint"""
        print("🔍 Testing backend health...")
        try:
            response = await self.client.get(f"{BACKEND_URL}/health")
            if response.status_code == 200:
                print("✅ Backend health check passed")
                return True
            else:
                print(f"❌ Backend health check failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Backend connection failed: {str(e)}")
            return False
    
    async def test_frontend_health(self):
        """Test frontend health"""
        print("🔍 Testing frontend health...")
        try:
            response = await self.client.get(f"{FRONTEND_URL}/")
            if response.status_code == 200:
                print("✅ Frontend health check passed")
                return True
            else:
                print(f"❌ Frontend health check failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Frontend connection failed: {str(e)}")
            return False
    
    async def test_user_registration(self):
        """Test user registration"""
        print("🔍 Testing user registration...")
        try:
            user_data = {
                "email": "test@example.com",
                "password": "TestPassword123!",
                "first_name": "Test",
                "last_name": "User",
                "role": "practitioner"
            }
            
            response = await self.client.post(
                f"{BACKEND_URL}/api/v1/auth/register",
                json=user_data
            )
            
            if response.status_code == 201:
                result = response.json()
                self.test_user_id = result["user"]["id"]
                print("✅ User registration passed")
                return True
            else:
                print(f"❌ User registration failed: {response.status_code}")
                print(f"Response: {response.text}")
                return False
        except Exception as e:
            print(f"❌ User registration error: {str(e)}")
            return False
    
    async def test_user_login(self):
        """Test user login"""
        print("🔍 Testing user login...")
        try:
            login_data = {
                "email": "test@example.com",
                "password": "TestPassword123!"
            }
            
            response = await self.client.post(
                f"{BACKEND_URL}/api/v1/auth/login",
                json=login_data
            )
            
            if response.status_code == 200:
                result = response.json()
                self.auth_token = result["access_token
                return True
            else:
                print(f"❌ User login failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ User login error: {str(e)}")
            return False
    
    async def test_protocol_creation(self):
        """Test protocol creation"""
        print("🔍 Testing protocol creation...")
        try:
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            protocol_data = {
                "name": "Test ADCI Protocol",
                "category": "surgical",
                "description": "Test protocol for ADCI validation",
                "version": "1.0",
                "applicable_stages": ["I", "II", "III"],
                "inclusion_criteria": ["Resectable gastric cancer", "ECOG 0-2"],
                "exclusion_criteria": ["Metastatic disease", "Previous gastric surgery"],
                "evidence_level": "1",
                "guidelines_source": "Test Guidelines 2024"
            }
            
            response = await self.client.post(
                f"{BACKEND_URL}/api/v1/protocols/",
                json=protocol_data,
                headers=headers
            )
            
            if response.status_code == 201:
                result = response.json()
                self.test_protocol_id = result["id"]
                print("✅ Protocol creation passed")
                return True
            else:
                print(f"❌ Protocol creation failed: {response.status_code}")
                print(f"Response: {response.text}")
                return False
        except Exception as e:
            print(f"❌ Protocol creation error: {str(e)}")
            return False
    
    async def test_patient_creation(self):
        """Test patient creation"""
        print("🔍 Testing patient creation...")
        try:
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            patient_data = {
                "first_name": "Test",
                "last_name": "Patient",
                "date_of_birth": "1970-01-01",
                "gender": "male",
                "medical_record_number": "TEST123456",
                "diagnosis_date": "2024-01-01",
                "stage": "II",
                "status": "active"
            }
            
            response = await self.client.post(
                f"{BACKEND_URL}/api/v1/patients/",
                json=patient_data,
                headers=headers
            )
            
            if response.status_code == 201:
                result = response.json()
                self.test_patient_id = result["id"]
                print("✅ Patient creation passed")
                return True
            else:
                print(f"❌ Patient creation failed: {response.status_code}")
                print(f"Response: {response.text}")
                return False
        except Exception as e:
            print(f"❌ Patient creation error: {str(e)}")
            return False
    
    async def test_decision_engine(self):
        """Test decision engine"""
        print("🔍 Testing decision engine...")
        try:
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            decision_data = {
                "patient_data": {
                    "age": 65,
                    "gender": "male",
                    "t_stage": "T3",
                    "n_stage": "N2",
                    "m_stage": "M0",
                    "ecog_status": 1,
                    "asa_score": 2,
                    "tumor_location": "distal",
                    "histology": "adenocarcinoma_intestinal"
                },
                "protocol_id": self.test_protocol_id
            }
            
            response = await self.client.post(
                f"{BACKEND_URL}/api/v1/decision-engine/process",
                json=decision_data,
                headers=headers
            )
            
            if response.status_code == 200:
                result = response.json()
                if "recommendations" in result and "confidence_score" in result:
                    print("✅ Decision engine test passed")
                    return True
                else:
                    print(f"❌ Decision engine returned incomplete data: {result}")
                    return False
            else:
                print(f"❌ Decision engine failed: {response.status_code}")
                print(f"Response: {response.text}")
                return False
        except Exception as e:
            print(f"❌ Decision engine error: {str(e)}")
            return False
    
    async def test_frontend_pages(self):
        """Test frontend pages"""
        print("🔍 Testing frontend pages...")
        try:
            pages = [
                ("/", "landing page"),
                ("/protocols", "protocols page"),
                ("/decision", "decision engine page")
            ]
            
            success_count = 0
            for path, name in pages:
                try:
                    response = await self.client.get(f"{FRONTEND_URL}{path}")
                    if response.status_code == 200:
                        print(f"✅ {name} accessible")
                        success_count += 1
                    else:
                        print(f"❌ {name} failed: {response.status_code}")
                except Exception as e:
                    print(f"❌ {name} error: {str(e)}")
            
            return success_count == len(pages)
        except Exception as e:
            print(f"❌ Frontend pages test error: {str(e)}")
            return False
    
    async def test_pwa_manifest(self):
        """Test PWA manifest"""
        print("🔍 Testing PWA manifest...")
        try:
            response = await self.client.get(f"{FRONTEND_URL}/manifest.json")
            if response.status_code == 200:
                manifest = response.json()
                if "name" in manifest and "start_url" in manifest:
                    print("✅ PWA manifest test passed")
                    return True
                else:
                    print(f"❌ PWA manifest incomplete: {manifest}")
                    return False
            else:
                print(f"❌ PWA manifest failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ PWA manifest error: {str(e)}")
            return False
    
    async def run_all_tests(self):
        """Run all tests"""
        print("🚀 Starting ADCI Platform Test Suite")
        print("=" * 50)
        
        tests = [
            ("Backend Health", self.test_backend_health),
            ("Frontend Health", self.test_frontend_health),
            ("User Registration", self.test_user_registration),
            ("User Login", self.test_user_login),
            ("Protocol Creation", self.test_protocol_creation),
            ("Patient Creation", self.test_patient_creation),
            ("Decision Engine", self.test_decision_engine),
            ("Frontend Pages", self.test_frontend_pages),
            ("PWA Manifest", self.test_pwa_manifest)
        ]
        
        passed = 0
        total = len(tests)
        
        for test_name, test_func in tests:
            print(f"\n📋 Running {test_name}...")
            try:
                if await test_func():
                    passed += 1
                else:
                    print(f"❌ {test_name} failed")
            except Exception as e:
                print(f"❌ {test_name} threw exception: {str(e)}")
        
        print("\n" + "=" * 50)
        print(f"🏁 Test Results: {passed}/{total} tests passed")
        
        if passed == total:
            print("🎉 All tests passed! ADCI Platform is ready.")
            return True
        else:
            print("⚠️ Some tests failed. Please check the issues above.")
            return False

async def main():
    """Main test function"""
    async with ADCITestSuite() as test_suite:
        success = await test_suite.run_all_tests()
        sys.exit(0 if success else 1)

if __name__ == "__main__":
    asyncio.run(main())
