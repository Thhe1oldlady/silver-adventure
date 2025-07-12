#!/usr/bin/env python3
"""
Email Service Test Script

This script tests the email service functionality, including template generation
and email sending capabilities.
"""

import sys
import os
import asyncio
from pathlib import Path

# Add src to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

from silver_adventure.services.email_service import EmailService


async def test_email_service():
    """Test the email service functionality"""
    print("🚀 Testing Silver Adventure Email Service")
    print("=" * 50)
    
    # Initialize service
    service = EmailService()
    
    # Test health check
    print("\n1. Testing health check...")
    health = service.health_check()
    print(f"   ✅ Health check: {'PASS' if health else 'FAIL'}")
    
    # Test available templates
    print("\n2. Testing available templates...")
    templates = service.get_available_templates()
    print(f"   ✅ Available templates: {templates}")
    
    # Test each template
    print("\n3. Testing template generation...")
    test_context = {
        "name": "John Doe",
        "email": "john@example.com",
        "company": "Silver Adventure",
        "quote": "Success is not final, failure is not fatal: it is the courage to continue that counts."
    }
    
    for template in templates:
        print(f"\n   Testing {template} template...")
        try:
            content = service._generate_golden_mood_content(template, test_context)
            
            # Validate content
            assert "html" in content, f"Missing HTML content for {template}"
            assert "text" in content, f"Missing text content for {template}"
            assert "subject" in content, f"Missing subject for {template}"
            
            assert len(content["html"]) > 100, f"HTML content too short for {template}"
            assert len(content["text"]) > 50, f"Text content too short for {template}"
            assert len(content["subject"]) > 5, f"Subject too short for {template}"
            
            # Check personalization
            assert test_context["name"] in content["html"], f"Name not found in HTML for {template}"
            assert test_context["name"] in content["text"], f"Name not found in text for {template}"
            
            print(f"   ✅ {template}: {content['subject']}")
            
        except Exception as e:
            print(f"   ❌ {template}: {str(e)}")
    
    # Test email sending (development mode)
    print("\n4. Testing email sending...")
    try:
        result = await service.send_golden_mood_email(
            to_email="test@example.com",
            template="welcome",
            context=test_context
        )
        
        assert "email_id" in result
        assert "status" in result
        assert "message" in result
        
        print(f"   ✅ Email sending test: {result['status']}")
        print(f"   📧 Email ID: {result['email_id']}")
        
    except Exception as e:
        print(f"   ❌ Email sending failed: {str(e)}")
    
    # Test custom subject
    print("\n5. Testing custom subject...")
    try:
        result = await service.send_golden_mood_email(
            to_email="test@example.com",
            template="celebration",
            subject="🎉 Custom Celebration Subject!",
            context=test_context
        )
        
        print(f"   ✅ Custom subject test: {result['status']}")
        
    except Exception as e:
        print(f"   ❌ Custom subject failed: {str(e)}")
    
    # Test color configuration
    print("\n6. Testing color configuration...")
    all_colors_valid = True
    
    for template_name, template_config in service.golden_mood_templates.items():
        colors = template_config.get("colors", {})
        
        for color_name, color_value in colors.items():
            if not (color_value.startswith("#") and len(color_value) == 7):
                print(f"   ❌ Invalid color in {template_name}.{color_name}: {color_value}")
                all_colors_valid = False
    
    if all_colors_valid:
        print("   ✅ All color configurations are valid")
    
    print("\n" + "=" * 50)
    print("✨ Email Service Test Complete!")
    print("🌟 All golden mood templates are ready to brighten your day!")


if __name__ == "__main__":
    asyncio.run(test_email_service())