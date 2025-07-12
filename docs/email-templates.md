# Silver Adventure - Email Templates Guide

## Overview

The Silver Adventure email system provides 6 beautifully designed "Golden Mood" templates that can be used for various communication needs. Each template is fully customizable with themes, colors, and personalization options.

## Available Templates

### 1. Welcome Template
**Purpose**: Onboarding new users or customers
**Theme**: Warm, friendly, inviting
**Best For**: New user registration, account activation, first-time greetings

**Example Usage**:
```python
from silver_adventure.services.email_service import EmailService

service = EmailService()
await service.send_golden_mood_email(
    to_email="user@example.com",
    template="welcome",
    context={
        "name": "John Doe",
        "company": "Acme Corp"
    }
)
```

### 2. Celebration Template
**Purpose**: Celebrating achievements and milestones
**Theme**: Joyful, congratulatory, festive
**Best For**: Goal completion, anniversaries, achievements, promotions

**Example Usage**:
```python
await service.send_golden_mood_email(
    to_email="user@example.com",
    template="celebration",
    context={
        "name": "Sarah Smith",
        "achievement": "completing your first project",
        "milestone": "1 year with us"
    }
)
```

### 3. Motivation Template
**Purpose**: Inspiring and encouraging users
**Theme**: Energetic, inspiring, uplifting
**Best For**: Daily motivation, goal setting, overcoming challenges

**Example Usage**:
```python
await service.send_golden_mood_email(
    to_email="user@example.com",
    template="motivation",
    context={
        "name": "Mike Johnson",
        "quote": "Your only limit is your mind",
        "goal": "launching your new project"
    }
)
```

### 4. Appreciation Template
**Purpose**: Showing gratitude and recognition
**Theme**: Heartfelt, grateful, warm
**Best For**: Thank you messages, recognition, customer appreciation

**Example Usage**:
```python
await service.send_golden_mood_email(
    to_email="user@example.com",
    template="appreciation",
    context={
        "name": "Emma Davis",
        "contribution": "your valuable feedback",
        "impact": "helped us improve our product"
    }
)
```

### 5. Opportunity Template
**Purpose**: Presenting new opportunities and offers
**Theme**: Exciting, urgent, valuable
**Best For**: Product launches, special offers, exclusive invitations

**Example Usage**:
```python
await service.send_golden_mood_email(
    to_email="user@example.com",
    template="opportunity",
    context={
        "name": "Alex Chen",
        "opportunity": "exclusive early access",
        "benefit": "50% discount on premium features",
        "deadline": "limited time offer"
    }
)
```

### 6. Newsletter Template
**Purpose**: Regular updates and communication
**Theme**: Informative, professional, engaging
**Best For**: Monthly updates, company news, feature announcements

**Example Usage**:
```python
await service.send_golden_mood_email(
    to_email="user@example.com",
    template="newsletter",
    context={
        "name": "Team",
        "highlights": ["New feature launch", "Customer success story"],
        "upcoming": "Webinar next week",
        "tips": "How to maximize your productivity"
    }
)
```

## Template Customization

### Color Schemes
Each template has its own color palette:

```python
# Template color configurations
templates = {
    "welcome": {
        "primary": "#FFD700",    # Gold
        "secondary": "#FFA500",  # Orange
        "accent": "#FF6B35"      # Red-Orange
    },
    "celebration": {
        "primary": "#FFD700",    # Gold
        "secondary": "#FF1493",  # Deep Pink
        "accent": "#9370DB"      # Medium Purple
    },
    "motivation": {
        "primary": "#FFD700",    # Gold
        "secondary": "#32CD32",  # Lime Green
        "accent": "#1E90FF"      # Dodger Blue
    },
    # ... and so on
}
```

### Context Variables
All templates support these common variables:

| Variable | Description | Default |
|----------|-------------|---------|
| `name` | Recipient's name | "Friend" |
| `sender_name` | Sender's name | "Silver Adventure Team" |
| `company` | Company name | - |
| `date` | Current date | Auto-generated |
| `custom_message` | Additional message | - |

### Advanced Customization

#### Custom Subject Lines
```python
await service.send_golden_mood_email(
    to_email="user@example.com",
    template="welcome",
    subject="🎉 Custom Welcome Message!",
    context={"name": "John"}
)
```

#### Template-Specific Variables
Each template accepts specific context variables:

**Welcome Template**:
- `onboarding_steps`: List of next steps
- `welcome_bonus`: Special offer for new users

**Celebration Template**:
- `achievement`: What is being celebrated
- `milestone`: Specific milestone reached
- `reward`: Special reward or recognition

**Motivation Template**:
- `quote`: Inspirational quote
- `goal`: Current goal or objective
- `progress`: Progress made so far

## API Integration

### REST API Endpoints

**Send Email**:
```http
POST /api/v1/email/send
Content-Type: application/json

{
    "to_email": "user@example.com",
    "template": "welcome",
    "subject": "Custom Subject (optional)",
    "context": {
        "name": "John Doe",
        "company": "Acme Corp"
    }
}
```

**Get Available Templates**:
```http
GET /api/v1/email/templates
```

Response:
```json
{
    "templates": [
        "welcome",
        "celebration",
        "motivation",
        "appreciation",
        "opportunity",
        "newsletter"
    ]
}
```

### Programmatic Usage

```python
from silver_adventure.services.email_service import EmailService

# Initialize service
service = EmailService()

# Get available templates
templates = service.get_available_templates()

# Send email with template
result = await service.send_golden_mood_email(
    to_email="recipient@example.com",
    template="welcome",
    context={"name": "John Doe"}
)

# Check result
if result["status"] == "sent":
    print(f"Email sent successfully! ID: {result['email_id']}")
```

## Email Configuration

### SMTP Setup
Configure your email settings in `.env`:

```env
# Email Configuration
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
FROM_EMAIL=noreply@your-domain.com
```

### Development Mode
For development, emails are logged instead of sent:

```python
# No SMTP configuration needed for development
# Emails will be logged to console
```

## Best Practices

### 1. Template Selection
- **Welcome**: First interaction, onboarding
- **Celebration**: Milestones, achievements
- **Motivation**: Regular engagement, challenges
- **Appreciation**: Retention, loyalty
- **Opportunity**: Sales, promotions
- **Newsletter**: Regular updates

### 2. Personalization
- Always include the recipient's name
- Use relevant context variables
- Customize the subject line when appropriate
- Include specific details about the user's situation

### 3. Content Guidelines
- Keep messages concise and focused
- Use clear call-to-action buttons
- Maintain consistent branding
- Test templates before sending

### 4. Technical Considerations
- Validate email addresses
- Handle SMTP errors gracefully
- Use proper HTML structure
- Provide plain text alternatives
- Monitor delivery rates

## Troubleshooting

### Common Issues

**1. Email Not Sending**
- Check SMTP configuration
- Verify credentials
- Test connection
- Review logs

**2. Template Rendering Issues**
- Validate context variables
- Check template syntax
- Review HTML structure
- Test with minimal context

**3. Formatting Problems**
- Verify HTML validity
- Check CSS compatibility
- Test across email clients
- Use email testing tools

### Testing Templates

```python
# Test template generation
content = service._generate_golden_mood_content("welcome", {"name": "Test"})
print(content["subject"])
print(content["html"][:100])  # First 100 characters
```

## Extending Templates

### Adding New Templates
1. Add template configuration to `golden_mood_templates`
2. Create HTML generation method
3. Create text generation method
4. Add to template list
5. Test thoroughly

### Template Structure
```python
def _create_custom_template(self, context: Dict[str, Any]) -> str:
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            /* Custom styles */
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Hello {context['name']}!</h1>
            <!-- Custom content -->
        </div>
    </body>
    </html>
    """
```

## Resources

- [Email HTML Best Practices](https://templates.mailchimp.com/development/html/)
- [Email Client Compatibility](https://www.campaignmonitor.com/css/)
- [SMTP Configuration Guide](https://support.google.com/accounts/answer/185833)
- [Email Testing Tools](https://litmus.com/)