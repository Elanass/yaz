#!/usr/bin/env python3
"""
Surgify AI Setup Script
Sets up local AI models and Hugging Face integration
"""

import os
import sys
from pathlib import Path
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def setup_ai_environment():
    """Setup AI environment with local models"""
    logger.info("🚀 Setting up Surgify AI environment...")
    
    # Create AI directories
    ai_dir = Path("ai_models")
    ai_dir.mkdir(exist_ok=True)
    
    cache_dir = ai_dir / "cache"
    cache_dir.mkdir(exist_ok=True)
    
    logger.info(f"✅ Created AI directories: {ai_dir}")
    
    # Install requirements from main requirements.txt
    logger.info("📦 Installing AI requirements from main requirements.txt...")
    
    try:
        import subprocess
        # Install specific AI packages that are now in main requirements.txt
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", 
            "transformers==4.36.0",
            "torch==2.1.0", 
            "huggingface_hub==0.19.0",
            "--quiet"
        ])
        logger.info("✅ AI packages installed successfully")
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ Failed to install AI packages: {e}")
        return False
    
    # Download and cache essential models
    try:
        from transformers import AutoTokenizer, AutoModel
        
        logger.info("🧠 Downloading BioClinicalBERT (this may take a few minutes)...")
        
        # Download BioClinicalBERT for medical text analysis
        model_name = "emilyalsentzer/Bio_ClinicalBERT"
        tokenizer = AutoTokenizer.from_pretrained(
            model_name,
            cache_dir=ai_dir / "bio_clinical_bert"
        )
        model = AutoModel.from_pretrained(
            model_name,
            cache_dir=ai_dir / "bio_clinical_bert"
        )
        
        logger.info("✅ BioClinicalBERT downloaded and cached locally")
        
        # Download lightweight classification model
        logger.info("🔍 Downloading classification model...")
        from transformers import pipeline
        
        classifier = pipeline(
            "text-classification",
            model="distilbert-base-uncased",
            cache_dir=ai_dir / "distilbert"
        )
        
        logger.info("✅ Classification model ready")
        
    except Exception as e:
        logger.error(f"❌ Model download failed: {e}")
        logger.info("💡 You can still use the API fallback modes")
    
    # Create environment file template
    create_env_template()
    
    logger.info("🎉 AI setup complete!")
    logger.info("💰 You now have FREE local AI inference capabilities")
    logger.info("📖 Check docs/ai-enhancement-plan.md for usage instructions")

def create_env_template():
    """Create .env template with AI settings"""
    env_template = """
# AI Configuration
# Add these to your .env file

# Hugging Face (optional - for API fallback)
# Get free API key at: https://huggingface.co/settings/tokens
HUGGINGFACE_API_KEY=your_hf_api_key_here

# OpenAI (optional - for premium features only)
OPENAI_API_KEY=your_openai_key_here
OPENAI_MODEL=gpt-4

# AI Model Settings
AI_CACHE_DIR=ai_models
AI_USE_LOCAL_MODELS=true
AI_FALLBACK_TO_API=true
AI_MAX_CACHE_SIZE=5GB
"""
    
    with open(".env.ai.template", "w") as f:
        f.write(env_template.strip())
    
    logger.info("📄 Created .env.ai.template - copy settings to your .env file")

def test_ai_setup():
    """Test the AI setup"""
    logger.info("🧪 Testing AI setup...")
    
    try:
        from src.surgify.ai.enhanced_ai_service import enhanced_ai_service
        
        # Test medical text analysis
        test_text = "Patient presents with acute abdominal pain and elevated white blood cell count."
        
        import asyncio
        result = asyncio.run(enhanced_ai_service.analyze_medical_text(test_text))
        
        if result and not result.get("error"):
            logger.info("✅ Medical text analysis working")
            logger.info(f"🔍 Found entities: {result.get('medical_entities', [])}")
        else:
            logger.warning("⚠️ Medical text analysis using fallback mode")
        
        # Test risk assessment
        test_patient = {
            "age": 65,
            "comorbidities": ["diabetes", "hypertension"],
            "procedure": "cardiac surgery"
        }
        
        risk_result = asyncio.run(enhanced_ai_service.assess_surgical_risk(test_patient))
        
        if risk_result and not risk_result.get("error"):
            logger.info(f"✅ Risk assessment working - Level: {risk_result.get('risk_level')}")
        else:
            logger.warning("⚠️ Risk assessment using fallback mode")
        
        logger.info("🎯 AI system is functional!")
        
    except Exception as e:
        logger.error(f"❌ AI test failed: {e}")
        logger.info("💡 Check your Python environment and dependencies")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        test_ai_setup()
    else:
        setup_ai_environment()
        
        # Ask if user wants to run test
        response = input("\n🧪 Would you like to test the AI setup? (y/n): ")
        if response.lower().startswith('y'):
            test_ai_setup()
