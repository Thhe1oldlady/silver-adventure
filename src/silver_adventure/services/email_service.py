"""
Email Service - Golden Mood Email Generation

This service handles the generation and sending of emails with customizable
"golden mood" themes. It includes various templates and personalization options.
"""

import logging
import os
import smtplib
import uuid
from datetime import datetime
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Any, Dict, List, Optional

from jinja2 import Environment, FileSystemLoader, select_autoescape

logger = logging.getLogger(__name__)


class EmailService:
    """Service for sending golden mood emails with customizable templates"""

    def __init__(self):
        self.smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.smtp_username = os.getenv("SMTP_USERNAME", "")
        self.smtp_password = os.getenv("SMTP_PASSWORD", "")
        self.from_email = os.getenv("FROM_EMAIL", "noreply@silver-adventure.com")

        # Initialize Jinja2 environment
        template_dir = os.path.join(
            os.path.dirname(__file__), "..", "templates", "email"
        )
        self.jinja_env = Environment(
            loader=(
                FileSystemLoader(template_dir) if os.path.exists(template_dir) else None
            ),
            autoescape=select_autoescape(["html", "xml"]),
        )

        # Golden mood templates
        self.golden_mood_templates = {
            "welcome": {
                "subject": "🌟 Welcome to Your Golden Journey! ✨",
                "theme": "warm_welcome",
                "colors": {
                    "primary": "#FFD700",
                    "secondary": "#FFA500",
                    "accent": "#FF6B35",
                },
            },
            "celebration": {
                "subject": "🎉 Time to Celebrate Your Success! 🏆",
                "theme": "celebration",
                "colors": {
                    "primary": "#FFD700",
                    "secondary": "#FF1493",
                    "accent": "#9370DB",
                },
            },
            "motivation": {
                "subject": "💪 Your Daily Dose of Golden Motivation ⚡",
                "theme": "motivation",
                "colors": {
                    "primary": "#FFD700",
                    "secondary": "#32CD32",
                    "accent": "#1E90FF",
                },
            },
            "appreciation": {
                "subject": "🙏 You're Simply Amazing! 💖",
                "theme": "appreciation",
                "colors": {
                    "primary": "#FFD700",
                    "secondary": "#FF69B4",
                    "accent": "#FF1493",
                },
            },
            "opportunity": {
                "subject": "🚀 Golden Opportunity Awaits You! 🌟",
                "theme": "opportunity",
                "colors": {
                    "primary": "#FFD700",
                    "secondary": "#00CED1",
                    "accent": "#FF4500",
                },
            },
            "newsletter": {
                "subject": "📰 Your Golden Newsletter is Here! ✨",
                "theme": "newsletter",
                "colors": {
                    "primary": "#FFD700",
                    "secondary": "#4169E1",
                    "accent": "#DC143C",
                },
            },
        }

    def health_check(self) -> bool:
        """Check if email service is healthy"""
        try:
            # Basic configuration check
            if not self.smtp_server or not self.from_email:
                return False
            return True
        except Exception as e:
            logger.error(f"Email service health check failed: {str(e)}")
            return False

    def get_available_templates(self) -> List[str]:
        """Get list of available email templates"""
        return list(self.golden_mood_templates.keys())

    def _generate_golden_mood_content(
        self, template: str, context: Dict[str, Any]
    ) -> Dict[str, str]:
        """Generate golden mood email content based on template"""
        template_config = self.golden_mood_templates.get(
            template, self.golden_mood_templates["welcome"]
        )

        # Default context values
        default_context = {
            "recipient_name": context.get("name", "Friend"),
            "sender_name": "Silver Adventure Team",
            "date": datetime.now().strftime("%B %d, %Y"),
            "year": datetime.now().year,
            "colors": template_config["colors"],
            "theme": template_config["theme"],
        }

        # Merge with provided context
        merged_context = {**default_context, **context}

        # Template-specific content generation
        if template == "welcome":
            html_content = self._create_welcome_template(merged_context)
            text_content = self._create_welcome_text(merged_context)
        elif template == "celebration":
            html_content = self._create_celebration_template(merged_context)
            text_content = self._create_celebration_text(merged_context)
        elif template == "motivation":
            html_content = self._create_motivation_template(merged_context)
            text_content = self._create_motivation_text(merged_context)
        elif template == "appreciation":
            html_content = self._create_appreciation_template(merged_context)
            text_content = self._create_appreciation_text(merged_context)
        elif template == "opportunity":
            html_content = self._create_opportunity_template(merged_context)
            text_content = self._create_opportunity_text(merged_context)
        elif template == "newsletter":
            html_content = self._create_newsletter_template(merged_context)
            text_content = self._create_newsletter_text(merged_context)
        else:
            html_content = self._create_welcome_template(merged_context)
            text_content = self._create_welcome_text(merged_context)

        return {
            "html": html_content,
            "text": text_content,
            "subject": template_config["subject"],
        }

    def _create_welcome_template(self, context: Dict[str, Any]) -> str:
        """Create welcome email HTML template"""
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Welcome to Silver Adventure</title>
            <style>
                body {{ font-family: 'Arial', sans-serif; margin: 0; padding: 0; background: linear-gradient(135deg, {context['colors']['primary']} 0%, {context['colors']['secondary']} 100%); }}
                .container {{ max-width: 600px; margin: 0 auto; background: white; border-radius: 10px; overflow: hidden; box-shadow: 0 10px 30px rgba(0,0,0,0.1); }}
                .header {{ background: linear-gradient(135deg, {context['colors']['primary']} 0%, {context['colors']['secondary']} 100%); padding: 40px; text-align: center; color: white; }}
                .content {{ padding: 40px; }}
                .footer {{ background: #f8f9fa; padding: 20px; text-align: center; color: #666; }}
                .button {{ display: inline-block; padding: 12px 30px; background: {context['colors']['accent']}; color: white; text-decoration: none; border-radius: 25px; margin: 20px 0; }}
                .highlight {{ color: {context['colors']['primary']}; font-weight: bold; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🌟 Welcome {context['recipient_name']}! ✨</h1>
                    <p>Your golden journey begins now!</p>
                </div>
                <div class="content">
                    <p>Dear <span class="highlight">{context['recipient_name']}</span>,</p>
                    <p>We're absolutely thrilled to welcome you to the Silver Adventure family! Your journey into a world of possibilities starts today.</p>
                    <p>Here's what makes your experience <strong>golden</strong>:</p>
                    <ul>
                        <li>✨ Personalized experiences just for you</li>
                        <li>🚀 Cutting-edge tools and features</li>
                        <li>💫 24/7 support from our amazing team</li>
                        <li>🎯 Opportunities to grow and succeed</li>
                    </ul>
                    <p>Ready to explore? Click the button below to get started!</p>
                    <a href="#" class="button">Start Your Journey 🚀</a>
                    <p>If you have any questions, don't hesitate to reach out. We're here to make your experience absolutely golden!</p>
                </div>
                <div class="footer">
                    <p>With golden regards,<br>The Silver Adventure Team</p>
                    <p><em>Making every moment shine! ✨</em></p>
                </div>
            </div>
        </body>
        </html>
        """

    def _create_welcome_text(self, context: Dict[str, Any]) -> str:
        """Create welcome email text template"""
        return f"""
        🌟 Welcome {context['recipient_name']}! ✨
        
        Dear {context['recipient_name']},
        
        We're absolutely thrilled to welcome you to the Silver Adventure family! Your journey into a world of possibilities starts today.
        
        Here's what makes your experience golden:
        • ✨ Personalized experiences just for you
        • 🚀 Cutting-edge tools and features
        • 💫 24/7 support from our amazing team
        • 🎯 Opportunities to grow and succeed
        
        Ready to explore? Visit our platform to get started!
        
        If you have any questions, don't hesitate to reach out. We're here to make your experience absolutely golden!
        
        With golden regards,
        The Silver Adventure Team
        
        Making every moment shine! ✨
        """

    def _create_celebration_template(self, context: Dict[str, Any]) -> str:
        """Create celebration email HTML template"""
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Time to Celebrate!</title>
            <style>
                body {{ font-family: 'Arial', sans-serif; margin: 0; padding: 0; background: linear-gradient(135deg, {context['colors']['primary']} 0%, {context['colors']['secondary']} 100%); }}
                .container {{ max-width: 600px; margin: 0 auto; background: white; border-radius: 10px; overflow: hidden; box-shadow: 0 10px 30px rgba(0,0,0,0.1); }}
                .header {{ background: linear-gradient(135deg, {context['colors']['primary']} 0%, {context['colors']['secondary']} 100%); padding: 40px; text-align: center; color: white; }}
                .content {{ padding: 40px; }}
                .footer {{ background: #f8f9fa; padding: 20px; text-align: center; color: #666; }}
                .celebration {{ font-size: 24px; text-align: center; margin: 20px 0; }}
                .highlight {{ color: {context['colors']['primary']}; font-weight: bold; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🎉 Time to Celebrate! 🏆</h1>
                    <p>Your success deserves recognition!</p>
                </div>
                <div class="content">
                    <div class="celebration">🎊 🎈 🎁 🎊 🎈 🎁 🎊</div>
                    <p>Dear <span class="highlight">{context['recipient_name']}</span>,</p>
                    <p>What an incredible achievement! Today is your day to shine, and we couldn't be prouder of your success.</p>
                    <p>Your dedication, hard work, and golden spirit have brought you to this moment. It's time to celebrate!</p>
                    <p>Here's to your amazing accomplishment and the bright future ahead! 🌟</p>
                    <div class="celebration">🎊 🎈 🎁 🎊 🎈 🎁 🎊</div>
                </div>
                <div class="footer">
                    <p>Celebrating with you,<br>The Silver Adventure Team</p>
                    <p><em>Your success is our golden moment! ✨</em></p>
                </div>
            </div>
        </body>
        </html>
        """

    def _create_celebration_text(self, context: Dict[str, Any]) -> str:
        """Create celebration email text template"""
        return f"""
        🎉 Time to Celebrate! 🏆
        
        Dear {context['recipient_name']},
        
        What an incredible achievement! Today is your day to shine, and we couldn't be prouder of your success.
        
        Your dedication, hard work, and golden spirit have brought you to this moment. It's time to celebrate!
        
        Here's to your amazing accomplishment and the bright future ahead! 🌟
        
        Celebrating with you,
        The Silver Adventure Team
        
        Your success is our golden moment! ✨
        """

    def _create_motivation_template(self, context: Dict[str, Any]) -> str:
        """Create motivation email HTML template"""
        motivation_quotes = [
            "The only way to do great work is to love what you do.",
            "Success is not final, failure is not fatal: it is the courage to continue that counts.",
            "The future belongs to those who believe in the beauty of their dreams.",
            "Your limitation—it's only your imagination.",
            "Push yourself, because no one else is going to do it for you.",
        ]

        quote = context.get("quote", motivation_quotes[0])

        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Daily Golden Motivation</title>
            <style>
                body {{ font-family: 'Arial', sans-serif; margin: 0; padding: 0; background: linear-gradient(135deg, {context['colors']['primary']} 0%, {context['colors']['secondary']} 100%); }}
                .container {{ max-width: 600px; margin: 0 auto; background: white; border-radius: 10px; overflow: hidden; box-shadow: 0 10px 30px rgba(0,0,0,0.1); }}
                .header {{ background: linear-gradient(135deg, {context['colors']['primary']} 0%, {context['colors']['secondary']} 100%); padding: 40px; text-align: center; color: white; }}
                .content {{ padding: 40px; }}
                .quote {{ font-size: 20px; font-style: italic; text-align: center; margin: 30px 0; padding: 20px; background: #f8f9fa; border-left: 4px solid {context['colors']['primary']}; }}
                .highlight {{ color: {context['colors']['primary']}; font-weight: bold; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>💪 Daily Golden Motivation ⚡</h1>
                    <p>Fuel your day with golden energy!</p>
                </div>
                <div class="content">
                    <p>Good morning, <span class="highlight">{context['recipient_name']}</span>!</p>
                    <p>Every sunrise brings new possibilities, and today is your chance to make something amazing happen.</p>
                    <div class="quote">
                        "{quote}"
                    </div>
                    <p>Remember: You have the power to turn your dreams into reality. Every step you take, every challenge you overcome, every goal you achieve - it all starts with believing in yourself.</p>
                    <p>Today's golden actions:</p>
                    <ul>
                        <li>🎯 Set one clear goal for today</li>
                        <li>✨ Take action, no matter how small</li>
                        <li>🚀 Celebrate your progress</li>
                        <li>💫 Share your positivity with others</li>
                    </ul>
                    <p>You've got this! Make today golden! 🌟</p>
                </div>
                <div class="footer">
                    <p>Cheering you on,<br>The Silver Adventure Team</p>
                    <p><em>Your potential is limitless! ✨</em></p>
                </div>
            </div>
        </body>
        </html>
        """

    def _create_motivation_text(self, context: Dict[str, Any]) -> str:
        """Create motivation email text template"""
        return f"""
        💪 Daily Golden Motivation ⚡
        
        Good morning, {context['recipient_name']}!
        
        Every sunrise brings new possibilities, and today is your chance to make something amazing happen.
        
        Remember: You have the power to turn your dreams into reality. Every step you take, every challenge you overcome, every goal you achieve - it all starts with believing in yourself.
        
        Today's golden actions:
        • 🎯 Set one clear goal for today
        • ✨ Take action, no matter how small
        • 🚀 Celebrate your progress
        • 💫 Share your positivity with others
        
        You've got this! Make today golden! 🌟
        
        Cheering you on,
        The Silver Adventure Team
        
        Your potential is limitless! ✨
        """

    def _create_appreciation_template(self, context: Dict[str, Any]) -> str:
        """Create appreciation email HTML template"""
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>You're Amazing!</title>
            <style>
                body {{ font-family: 'Arial', sans-serif; margin: 0; padding: 0; background: linear-gradient(135deg, {context['colors']['primary']} 0%, {context['colors']['secondary']} 100%); }}
                .container {{ max-width: 600px; margin: 0 auto; background: white; border-radius: 10px; overflow: hidden; box-shadow: 0 10px 30px rgba(0,0,0,0.1); }}
                .header {{ background: linear-gradient(135deg, {context['colors']['primary']} 0%, {context['colors']['secondary']} 100%); padding: 40px; text-align: center; color: white; }}
                .content {{ padding: 40px; }}
                .hearts {{ font-size: 24px; text-align: center; margin: 20px 0; }}
                .highlight {{ color: {context['colors']['primary']}; font-weight: bold; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🙏 You're Simply Amazing! 💖</h1>
                    <p>A heartfelt thank you just for you!</p>
                </div>
                <div class="content">
                    <div class="hearts">💖 💫 🌟 💖 💫 🌟 💖</div>
                    <p>Dear <span class="highlight">{context['recipient_name']}</span>,</p>
                    <p>Sometimes we get so busy with life that we forget to pause and appreciate the wonderful people around us. Today, we're taking that moment to appreciate YOU!</p>
                    <p>Your kindness, your spirit, and your unique way of brightening the world don't go unnoticed. You make a difference, and that's something truly special.</p>
                    <p>Thank you for being exactly who you are. Thank you for your golden heart and the positive energy you bring to everything you do.</p>
                    <p>The world is a better place because you're in it! 🌍✨</p>
                    <div class="hearts">💖 💫 🌟 💖 💫 🌟 💖</div>
                </div>
                <div class="footer">
                    <p>With heartfelt appreciation,<br>The Silver Adventure Team</p>
                    <p><em>You're one in a million! ✨</em></p>
                </div>
            </div>
        </body>
        </html>
        """

    def _create_appreciation_text(self, context: Dict[str, Any]) -> str:
        """Create appreciation email text template"""
        return f"""
        🙏 You're Simply Amazing! 💖
        
        Dear {context['recipient_name']},
        
        Sometimes we get so busy with life that we forget to pause and appreciate the wonderful people around us. Today, we're taking that moment to appreciate YOU!
        
        Your kindness, your spirit, and your unique way of brightening the world don't go unnoticed. You make a difference, and that's something truly special.
        
        Thank you for being exactly who you are. Thank you for your golden heart and the positive energy you bring to everything you do.
        
        The world is a better place because you're in it! 🌍✨
        
        With heartfelt appreciation,
        The Silver Adventure Team
        
        You're one in a million! ✨
        """

    def _create_opportunity_template(self, context: Dict[str, Any]) -> str:
        """Create opportunity email HTML template"""
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Golden Opportunity Awaits!</title>
            <style>
                body {{ font-family: 'Arial', sans-serif; margin: 0; padding: 0; background: linear-gradient(135deg, {context['colors']['primary']} 0%, {context['colors']['secondary']} 100%); }}
                .container {{ max-width: 600px; margin: 0 auto; background: white; border-radius: 10px; overflow: hidden; box-shadow: 0 10px 30px rgba(0,0,0,0.1); }}
                .header {{ background: linear-gradient(135deg, {context['colors']['primary']} 0%, {context['colors']['secondary']} 100%); padding: 40px; text-align: center; color: white; }}
                .content {{ padding: 40px; }}
                .cta {{ background: {context['colors']['accent']}; color: white; padding: 15px 30px; text-decoration: none; border-radius: 25px; display: inline-block; margin: 20px 0; }}
                .highlight {{ color: {context['colors']['primary']}; font-weight: bold; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🚀 Golden Opportunity Awaits! 🌟</h1>
                    <p>Your moment to shine is here!</p>
                </div>
                <div class="content">
                    <p>Dear <span class="highlight">{context['recipient_name']}</span>,</p>
                    <p>Some opportunities come once in a lifetime, and this is one of them! We're excited to share something special that could change your journey completely.</p>
                    <p>This golden opportunity offers you:</p>
                    <ul>
                        <li>🌟 Exclusive access to premium features</li>
                        <li>💎 Personalized guidance from experts</li>
                        <li>🚀 Fast-track to your goals</li>
                        <li>🎯 Proven strategies for success</li>
                    </ul>
                    <p>Don't let this golden moment slip away. Take action now and transform your future!</p>
                    <a href="#" class="cta">Seize Your Opportunity 🚀</a>
                    <p>Remember: Fortune favors the bold. This is your time to shine! ✨</p>
                </div>
                <div class="footer">
                    <p>Believing in your success,<br>The Silver Adventure Team</p>
                    <p><em>Your golden moment is now! ✨</em></p>
                </div>
            </div>
        </body>
        </html>
        """

    def _create_opportunity_text(self, context: Dict[str, Any]) -> str:
        """Create opportunity email text template"""
        return f"""
        🚀 Golden Opportunity Awaits! 🌟
        
        Dear {context['recipient_name']},
        
        Some opportunities come once in a lifetime, and this is one of them! We're excited to share something special that could change your journey completely.
        
        This golden opportunity offers you:
        • 🌟 Exclusive access to premium features
        • 💎 Personalized guidance from experts
        • 🚀 Fast-track to your goals
        • 🎯 Proven strategies for success
        
        Don't let this golden moment slip away. Take action now and transform your future!
        
        Remember: Fortune favors the bold. This is your time to shine! ✨
        
        Believing in your success,
        The Silver Adventure Team
        
        Your golden moment is now! ✨
        """

    def _create_newsletter_template(self, context: Dict[str, Any]) -> str:
        """Create newsletter email HTML template"""
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Your Golden Newsletter</title>
            <style>
                body {{ font-family: 'Arial', sans-serif; margin: 0; padding: 0; background: linear-gradient(135deg, {context['colors']['primary']} 0%, {context['colors']['secondary']} 100%); }}
                .container {{ max-width: 600px; margin: 0 auto; background: white; border-radius: 10px; overflow: hidden; box-shadow: 0 10px 30px rgba(0,0,0,0.1); }}
                .header {{ background: linear-gradient(135deg, {context['colors']['primary']} 0%, {context['colors']['secondary']} 100%); padding: 40px; text-align: center; color: white; }}
                .content {{ padding: 40px; }}
                .section {{ margin: 30px 0; padding: 20px; background: #f8f9fa; border-radius: 8px; }}
                .highlight {{ color: {context['colors']['primary']}; font-weight: bold; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>📰 Your Golden Newsletter ✨</h1>
                    <p>All the golden updates you need!</p>
                </div>
                <div class="content">
                    <p>Hello <span class="highlight">{context['recipient_name']}</span>,</p>
                    <p>Welcome to your golden newsletter! Here's what's shining bright in our community this week.</p>
                    
                    <div class="section">
                        <h3>🌟 This Week's Highlights</h3>
                        <ul>
                            <li>New features that will make your experience golden</li>
                            <li>Success stories from our amazing community</li>
                            <li>Upcoming events and opportunities</li>
                        </ul>
                    </div>
                    
                    <div class="section">
                        <h3>💡 Golden Tips</h3>
                        <p>Make the most of your Silver Adventure experience with these expert tips and tricks!</p>
                    </div>
                    
                    <div class="section">
                        <h3>🎯 What's Coming Next</h3>
                        <p>Exciting developments are on the horizon. Stay tuned for more golden opportunities!</p>
                    </div>
                    
                    <p>Thank you for being part of our golden community. Your engagement and enthusiasm make everything we do worthwhile!</p>
                </div>
                <div class="footer">
                    <p>Stay golden,<br>The Silver Adventure Team</p>
                    <p><em>Building golden experiences together! ✨</em></p>
                </div>
            </div>
        </body>
        </html>
        """

    def _create_newsletter_text(self, context: Dict[str, Any]) -> str:
        """Create newsletter email text template"""
        return f"""
        📰 Your Golden Newsletter ✨
        
        Hello {context['recipient_name']},
        
        Welcome to your golden newsletter! Here's what's shining bright in our community this week.
        
        🌟 This Week's Highlights:
        • New features that will make your experience golden
        • Success stories from our amazing community
        • Upcoming events and opportunities
        
        💡 Golden Tips:
        Make the most of your Silver Adventure experience with these expert tips and tricks!
        
        🎯 What's Coming Next:
        Exciting developments are on the horizon. Stay tuned for more golden opportunities!
        
        Thank you for being part of our golden community. Your engagement and enthusiasm make everything we do worthwhile!
        
        Stay golden,
        The Silver Adventure Team
        
        Building golden experiences together! ✨
        """

    async def send_golden_mood_email(
        self,
        to_email: str,
        template: str,
        subject: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Send a golden mood email"""
        try:
            # Generate email content
            content = self._generate_golden_mood_content(template, context or {})

            # Use custom subject if provided
            email_subject = subject or content["subject"]

            # Create email message
            msg = MIMEMultipart("alternative")
            msg["Subject"] = email_subject
            msg["From"] = self.from_email
            msg["To"] = to_email

            # Create text and HTML parts
            text_part = MIMEText(content["text"], "plain")
            html_part = MIMEText(content["html"], "html")

            # Attach parts
            msg.attach(text_part)
            msg.attach(html_part)

            # Generate email ID for tracking
            email_id = str(uuid.uuid4())

            # For development/testing, log the email instead of sending
            if not self.smtp_username or not self.smtp_password:
                logger.info(
                    f"Email would be sent to {to_email} with subject: {email_subject}"
                )
                logger.info(f"Email ID: {email_id}")
                return {
                    "email_id": email_id,
                    "status": "logged",
                    "message": "Email logged for development (no SMTP credentials)",
                }

            # Send email via SMTP
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_username, self.smtp_password)
                server.send_message(msg)

            logger.info(f"Email sent successfully to {to_email} with ID: {email_id}")

            return {
                "email_id": email_id,
                "status": "sent",
                "message": "Email sent successfully",
            }

        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {str(e)}")
            raise Exception(f"Email sending failed: {str(e)}")
