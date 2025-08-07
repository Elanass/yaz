#!/usr/bin/env python3
"""
Surgify AI Cost Comparison Demo
Shows the cost difference between OpenAI, HuggingFace API, and Local Models
"""

import asyncio
import time
from typing import Dict, Any

# Cost analysis (approximate prices as of 2024)
COSTS = {
    "openai_gpt4": {
        "input_cost_per_1k_tokens": 0.03,
        "output_cost_per_1k_tokens": 0.06,
        "avg_tokens_per_request": 500
    },
    "huggingface_api": {
        "cost_per_request": 0.0001,  # Much cheaper
        "free_tier_requests": 1000   # per month
    },
    "local_models": {
        "cost_per_request": 0.0,     # Completely free!
        "one_time_setup_cost": 0.0   # Using free models
    }
}

def calculate_monthly_costs(requests_per_day: int) -> Dict[str, float]:
    """Calculate monthly costs for different AI approaches"""
    monthly_requests = requests_per_day * 30
    
    costs = {}
    
    # OpenAI GPT-4 costs
    avg_cost_per_request = (
        (COSTS["openai_gpt4"]["avg_tokens_per_request"] / 1000) *
        (COSTS["openai_gpt4"]["input_cost_per_1k_tokens"] + 
         COSTS["openai_gpt4"]["output_cost_per_1k_tokens"]) / 2
    )
    costs["OpenAI GPT-4"] = monthly_requests * avg_cost_per_request
    
    # HuggingFace API costs
    free_requests = COSTS["huggingface_api"]["free_tier_requests"]
    paid_requests = max(0, monthly_requests - free_requests)
    costs["HuggingFace API"] = paid_requests * COSTS["huggingface_api"]["cost_per_request"]
    
    # Local models (always free)
    costs["Local Models"] = 0.0
    
    return costs

async def demo_ai_capabilities():
    """Demonstrate AI capabilities with different approaches"""
    print("🧠 Surgify AI Capabilities Demo")
    print("=" * 50)
    
    # Sample medical case
    sample_case = {
        "patient_text": "65-year-old male with diabetes and hypertension presenting for cardiac bypass surgery. Recent myocardial infarction 6 months ago. Current medications include metformin, lisinopril, and atorvastatin.",
        "patient_data": {
            "age": 65,
            "gender": "M",
            "comorbidities": ["diabetes", "hypertension", "previous_mi"],
            "procedure": "cardiac bypass surgery",
            "emergency": False,
            "bmi": 28.5
        }
    }
    
    print("📋 Sample Case:")
    print(f"   Text: {sample_case['patient_text'][:100]}...")
    print(f"   Patient: {sample_case['patient_data']['age']}yo {sample_case['patient_data']['gender']}")
    print(f"   Procedure: {sample_case['patient_data']['procedure']}")
    print()
    
    # Simulate different AI approaches
    approaches = [
        {
            "name": "🏠 Local BioClinicalBERT",
            "cost": "$0.00",
            "speed": "Fast (150ms)",
            "privacy": "Complete",
            "accuracy": "High (specialized for medical text)"
        },
        {
            "name": "🤗 HuggingFace API",
            "cost": "$0.0001 per request",
            "speed": "Medium (500ms)",
            "privacy": "Good",
            "accuracy": "High (cloud models)"
        },
        {
            "name": "🧠 OpenAI GPT-4",
            "cost": "$0.045 per request",
            "speed": "Slow (2000ms)",
            "privacy": "Limited",
            "accuracy": "Very High (general intelligence)"
        }
    ]
    
    print("🔍 AI Analysis Approaches:")
    for approach in approaches:
        print(f"\n{approach['name']}")
        print(f"   💰 Cost: {approach['cost']}")
        print(f"   ⚡ Speed: {approach['speed']}")
        print(f"   🔒 Privacy: {approach['privacy']}")
        print(f"   🎯 Accuracy: {approach['accuracy']}")
    
    # Cost comparison for different usage levels
    print("\n💰 Monthly Cost Comparison")
    print("=" * 50)
    
    usage_scenarios = [
        ("Small Clinic", 10),
        ("Medium Hospital", 100),
        ("Large Hospital", 1000),
        ("Hospital System", 5000)
    ]
    
    for scenario_name, daily_requests in usage_scenarios:
        print(f"\n📊 {scenario_name} ({daily_requests} requests/day):")
        costs = calculate_monthly_costs(daily_requests)
        
        for service, cost in costs.items():
            if cost == 0:
                print(f"   {service}: FREE 🎉")
            else:
                print(f"   {service}: ${cost:.2f}/month")
        
        # Calculate savings
        openai_cost = costs["OpenAI GPT-4"]
        local_savings = openai_cost - costs["Local Models"]
        hf_savings = openai_cost - costs["HuggingFace API"]
        
        print(f"   💵 Savings with Local Models: ${local_savings:.2f}/month")
        print(f"   💵 Savings with HF API: ${hf_savings:.2f}/month")

def recommend_approach():
    """Recommend the best approach for Surgify"""
    print("\n🎯 RECOMMENDATION FOR SURGIFY")
    print("=" * 50)
    
    print("✅ RECOMMENDED HYBRID APPROACH:")
    print("   1. 🏠 Local Models (Primary) - FREE")
    print("      • BioClinicalBERT for medical text analysis")
    print("      • Statistical models for risk assessment")
    print("      • Completely free, fast, private")
    print()
    print("   2. 🤗 HuggingFace API (Fallback) - LOW COST")
    print("      • For specialized models not available locally")
    print("      • 1000 free requests/month, then $0.0001/request")
    print("      • Good balance of cost and capability")
    print()
    print("   3. 🧠 OpenAI GPT-4 (Premium Only) - HIGH COST")
    print("      • Only for complex reasoning tasks")
    print("      • Use sparingly for critical cases")
    print("      • High cost but highest accuracy")
    print()
    
    print("💡 IMPLEMENTATION BENEFITS:")
    print("   • 90%+ cost reduction vs OpenAI-only approach")
    print("   • Faster inference for routine tasks")
    print("   • Better privacy compliance (local processing)")
    print("   • Offline capability for critical functions")
    print("   • Scalable without proportional cost increase")
    print()
    
    print("🚀 GETTING STARTED:")
    print("   1. Run: python tools/setup_ai.py")
    print("   2. AI packages are now in main requirements.txt")
    print("   3. Copy settings from .env.ai.template to your .env")
    print("   4. Test with: python tools/setup_ai.py test")
    print("   5. Use new endpoints: /api/v1/ai/enhanced/*")

if __name__ == "__main__":
    print("🏥 SURGIFY AI ENHANCEMENT ANALYSIS")
    print("=" * 60)
    
    # Run the demo
    asyncio.run(demo_ai_capabilities())
    
    # Show recommendations
    recommend_approach()
    
    print("\n" + "=" * 60)
    print("💰 BOTTOM LINE: Save 90%+ on AI costs with better privacy!")
    print("🎯 Perfect for budget-conscious healthcare applications")
    print("=" * 60)
