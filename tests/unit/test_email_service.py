"""
Unit tests for the Email Service
"""

import pytest
from unittest.mock import patch, MagicMock
from silver_adventure.services.email_service import EmailService


class TestEmailService:
    """Test cases for EmailService"""
    
    def test_health_check(self, email_service):
        """Test email service health check"""
        assert email_service.health_check() is True
    
    def test_get_available_templates(self, email_service):
        """Test getting available email templates"""
        templates = email_service.get_available_templates()
        
        assert isinstance(templates, list)
        assert len(templates) > 0
        assert "welcome" in templates
        assert "celebration" in templates
        assert "motivation" in templates
    
    def test_generate_welcome_content(self, email_service, sample_email_context):
        """Test generating welcome email content"""
        content = email_service._generate_golden_mood_content("welcome", sample_email_context)
        
        assert "html" in content
        assert "text" in content
        assert "subject" in content
        
        # Check that content contains expected elements
        assert sample_email_context["name"] in content["html"]
        assert sample_email_context["name"] in content["text"]
        assert "Welcome" in content["subject"]
    
    def test_generate_celebration_content(self, email_service, sample_email_context):
        """Test generating celebration email content"""
        content = email_service._generate_golden_mood_content("celebration", sample_email_context)
        
        assert "html" in content
        assert "text" in content
        assert "subject" in content
        
        # Check celebration-specific content
        assert "🎉" in content["subject"]
        assert "celebrate" in content["html"].lower()
    
    def test_generate_motivation_content(self, email_service, sample_email_context):
        """Test generating motivation email content"""
        content = email_service._generate_golden_mood_content("motivation", sample_email_context)
        
        assert "html" in content
        assert "text" in content
        assert "subject" in content
        
        # Check motivation-specific content
        assert "💪" in content["subject"]
        assert "motivation" in content["html"].lower()
    
    def test_generate_appreciation_content(self, email_service, sample_email_context):
        """Test generating appreciation email content"""
        content = email_service._generate_golden_mood_content("appreciation", sample_email_context)
        
        assert "html" in content
        assert "text" in content
        assert "subject" in content
        
        # Check appreciation-specific content
        assert "🙏" in content["subject"]
        assert "amazing" in content["html"].lower()
    
    def test_generate_opportunity_content(self, email_service, sample_email_context):
        """Test generating opportunity email content"""
        content = email_service._generate_golden_mood_content("opportunity", sample_email_context)
        
        assert "html" in content
        assert "text" in content
        assert "subject" in content
        
        # Check opportunity-specific content
        assert "🚀" in content["subject"]
        assert "opportunity" in content["html"].lower()
    
    def test_generate_newsletter_content(self, email_service, sample_email_context):
        """Test generating newsletter email content"""
        content = email_service._generate_golden_mood_content("newsletter", sample_email_context)
        
        assert "html" in content
        assert "text" in content
        assert "subject" in content
        
        # Check newsletter-specific content
        assert "📰" in content["subject"]
        assert "newsletter" in content["html"].lower()
    
    def test_generate_invalid_template(self, email_service, sample_email_context):
        """Test generating content with invalid template falls back to welcome"""
        content = email_service._generate_golden_mood_content("invalid_template", sample_email_context)
        
        assert "html" in content
        assert "text" in content
        assert "subject" in content
        
        # Should fallback to welcome template
        assert "Welcome" in content["subject"]
    
    @pytest.mark.asyncio
    async def test_send_email_without_smtp(self, email_service, sample_email_context):
        """Test sending email without SMTP configuration (development mode)"""
        result = await email_service.send_golden_mood_email(
            to_email="test@example.com",
            template="welcome",
            context=sample_email_context
        )
        
        assert "email_id" in result
        assert result["status"] == "logged"
        assert "message" in result
    
    @pytest.mark.asyncio
    async def test_send_email_with_custom_subject(self, email_service, sample_email_context):
        """Test sending email with custom subject"""
        custom_subject = "Custom Test Subject"
        
        result = await email_service.send_golden_mood_email(
            to_email="test@example.com",
            template="welcome",
            subject=custom_subject,
            context=sample_email_context
        )
        
        assert "email_id" in result
        assert result["status"] == "logged"
    
    def test_template_colors_configuration(self, email_service):
        """Test that all templates have proper color configuration"""
        for template_name in email_service.golden_mood_templates:
            template_config = email_service.golden_mood_templates[template_name]
            
            assert "colors" in template_config
            assert "primary" in template_config["colors"]
            assert "secondary" in template_config["colors"]
            assert "accent" in template_config["colors"]
            
            # Check that colors are valid hex codes
            for color_name, color_value in template_config["colors"].items():
                assert color_value.startswith("#")
                assert len(color_value) == 7  # #RRGGBB format
    
    def test_template_themes_configuration(self, email_service):
        """Test that all templates have proper theme configuration"""
        for template_name in email_service.golden_mood_templates:
            template_config = email_service.golden_mood_templates[template_name]
            
            assert "theme" in template_config
            assert "subject" in template_config
            assert isinstance(template_config["theme"], str)
            assert isinstance(template_config["subject"], str)
            assert len(template_config["subject"]) > 0