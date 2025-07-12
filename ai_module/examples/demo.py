#!/usr/bin/env python3
"""
Demo script for AI Module

This script demonstrates the capabilities of the AI module including
text processing, sentiment analysis, user interaction, and more.
"""

import sys
import os
from pathlib import Path

# Add the parent directory to the path to import ai_module
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from ai_module import AIBase, TextProcessor, UserInteraction, Config, Helper


def demonstrate_text_processing():
    """Demonstrate text processing capabilities."""
    print("=" * 60)
    print("TEXT PROCESSING DEMONSTRATION")
    print("=" * 60)
    
    # Sample text for analysis
    sample_text = """
    Artificial Intelligence is revolutionizing the way we interact with technology.
    It brings amazing possibilities for automation, analysis, and user experience.
    However, we must also consider the challenges and ethical implications.
    The future of AI looks bright, but we need to proceed with careful consideration.
    """
    
    # Initialize text processor
    text_processor = TextProcessor()
    
    print(f"Sample text: {sample_text.strip()}")
    print()
    
    # Tokenization
    tokens = text_processor.tokenize(sample_text)
    print(f"Tokens: {tokens[:10]}...")  # Show first 10 tokens
    print()
    
    # Sentiment analysis
    sentiment = text_processor.analyze_sentiment(sample_text)
    print(f"Sentiment Analysis:")
    print(f"  Sentiment: {sentiment['sentiment']}")
    print(f"  Confidence: {sentiment['confidence']:.2f}")
    print(f"  Positive words: {sentiment['scores']['positive']}")
    print(f"  Negative words: {sentiment['scores']['negative']}")
    print()
    
    # Keyword extraction
    keywords = text_processor.extract_keywords(sample_text, max_keywords=5)
    print(f"Top Keywords:")
    for i, (keyword, frequency) in enumerate(keywords, 1):
        print(f"  {i}. {keyword} ({frequency} times)")
    print()
    
    # Text statistics
    stats = text_processor.count_words(sample_text)
    print(f"Text Statistics:")
    for key, value in stats.items():
        if isinstance(value, float):
            print(f"  {key.replace('_', ' ').title()}: {value:.2f}")
        else:
            print(f"  {key.replace('_', ' ').title()}: {value}")
    print()
    
    # Text summarization
    summary = text_processor.summarize_text(sample_text, max_sentences=2)
    print(f"Summary: {summary}")
    print()


def demonstrate_user_interaction():
    """Demonstrate user interaction capabilities."""
    print("=" * 60)
    print("USER INTERACTION DEMONSTRATION")
    print("=" * 60)
    
    # Initialize user interaction handler
    user_interaction = UserInteraction()
    
    # Sample interactions
    interactions = [
        "Hello, I'm interested in learning about AI!",
        "Can you analyze this text: 'I love this new technology, it's amazing!'",
        "/sentiment This is a terrible experience, I hate it!",
        "/keywords Artificial intelligence, machine learning, and data science are transforming industries",
        "/help",
        "/stats The quick brown fox jumps over the lazy dog",
        "Thank you for your help!"
    ]
    
    print("Simulating user interactions:")
    print()
    
    for i, user_input in enumerate(interactions, 1):
        print(f"User {i}: {user_input}")
        
        response = user_interaction.process_user_input(user_input, user_id="demo_user")
        
        print(f"AI: {response['text']}")
        print(f"Response Type: {response['type']}")
        print("-" * 40)
    
    # Show conversation history
    history = user_interaction.get_conversation_history("demo_user")
    print(f"\nConversation History: {len(history)} interactions")
    print()


def demonstrate_configuration():
    """Demonstrate configuration management."""
    print("=" * 60)
    print("CONFIGURATION DEMONSTRATION")
    print("=" * 60)
    
    # Create configuration with custom settings
    custom_config = {
        "log_level": "DEBUG",
        "max_history_length": 50,
        "text_processing": {
            "remove_stopwords": False,
            "min_keyword_length": 2
        }
    }
    
    config = Config(custom_config)
    
    print("Configuration settings:")
    print(f"  Log Level: {config.get('log_level')}")
    print(f"  Max History Length: {config.get('max_history_length')}")
    print(f"  Remove Stopwords: {config.get('text_processing.remove_stopwords')}")
    print(f"  Min Keyword Length: {config.get('text_processing.min_keyword_length')}")
    print()
    
    # Validate configuration
    validation = config.validate()
    print(f"Configuration Valid: {validation['valid']}")
    if validation['issues']:
        print("Issues found:")
        for issue in validation['issues']:
            print(f"  - {issue}")
    print()


def demonstrate_helpers():
    """Demonstrate helper utilities."""
    print("=" * 60)
    print("HELPER UTILITIES DEMONSTRATION")
    print("=" * 60)
    
    # Generate unique ID
    unique_id = Helper.generate_id("demo", 8)
    print(f"Generated ID: {unique_id}")
    
    # Hash text
    sample_text = "This is a sample text for hashing"
    text_hash = Helper.hash_text(sample_text)
    print(f"Text Hash: {text_hash[:16]}...")
    
    # Validate email
    email = "user@example.com"
    is_valid_email = Helper.validate_email(email)
    print(f"Email '{email}' is valid: {is_valid_email}")
    
    # Format duration
    duration = Helper.format_duration(3665)  # 1 hour, 1 minute, 5 seconds
    print(f"Duration: {duration}")
    
    # Truncate text
    long_text = "This is a very long text that needs to be truncated"
    truncated = Helper.truncate_text(long_text, 30)
    print(f"Truncated: {truncated}")
    
    # Calculate similarity
    text1 = "I love artificial intelligence"
    text2 = "Artificial intelligence is amazing"
    similarity = Helper.calculate_similarity(text1, text2)
    print(f"Similarity between texts: {similarity:.2f}")
    
    print()


def demonstrate_ai_base():
    """Demonstrate AI base functionality."""
    print("=" * 60)
    print("AI BASE DEMONSTRATION")
    print("=" * 60)
    
    # Initialize AI base
    ai_base = AIBase()
    
    print(f"AI Base Version: {ai_base.version}")
    print(f"Created At: {ai_base.created_at}")
    print()
    
    # State management
    ai_base.update_state("demo_key", "demo_value")
    ai_base.update_state("counter", 42)
    
    print(f"State - demo_key: {ai_base.get_state('demo_key')}")
    print(f"State - counter: {ai_base.get_state('counter')}")
    print()
    
    # Get status
    status = ai_base.get_status()
    print("AI Base Status:")
    print(f"  Version: {status['version']}")
    print(f"  State Keys: {list(status['state'].keys())}")
    print()


def interactive_demo():
    """Run an interactive demo."""
    print("=" * 60)
    print("INTERACTIVE DEMO")
    print("=" * 60)
    
    print("Welcome to the AI Module Interactive Demo!")
    print("You can now interact with the AI module directly.")
    print("Type 'quit' to exit the demo.")
    print("Available commands: /help, /sentiment, /keywords, /summarize, /stats")
    print()
    
    user_interaction = UserInteraction()
    
    while True:
        try:
            user_input = input("You: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'bye']:
                print("AI: Goodbye! Thank you for trying the AI module demo.")
                break
            
            if not user_input:
                continue
            
            response = user_interaction.process_user_input(user_input, user_id="interactive_user")
            print(f"AI: {response['text']}")
            print()
            
        except KeyboardInterrupt:
            print("\nAI: Goodbye! Thank you for trying the AI module demo.")
            break
        except Exception as e:
            print(f"Error: {e}")
            print("Please try again.")


def main():
    """Main demo function."""
    print("🤖 AI MODULE DEMONSTRATION")
    print("=" * 60)
    print("This demo showcases the capabilities of the AI module")
    print("developed for the silver-adventure repository.")
    print()
    
    try:
        # Run demonstrations
        demonstrate_ai_base()
        demonstrate_text_processing()
        demonstrate_user_interaction()
        demonstrate_configuration()
        demonstrate_helpers()
        
        # Ask if user wants interactive demo
        print("Would you like to try the interactive demo? (y/n): ", end="")
        if input().lower().startswith('y'):
            interactive_demo()
        
        print("\n✅ Demo completed successfully!")
        print("The AI module is ready for integration with your applications.")
        
    except Exception as e:
        print(f"\n❌ Demo failed with error: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())