"""
User interaction handling for AI module.

This module provides functionality to handle user interactions, including
input processing, response generation, and conversation management.
"""

import json
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime
from .ai_base import AIBase
from .text_processor import TextProcessor


class UserInteraction(AIBase):
    """
    User interaction class for handling conversations and responses.
    
    This class manages user interactions, maintains conversation history,
    and provides response generation capabilities.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the UserInteraction handler.
        
        Args:
            config (Optional[Dict[str, Any]]): Configuration dictionary
        """
        super().__init__(config)
        self.text_processor = TextProcessor(config)
        self.conversation_history = []
        self.user_sessions = {}
        self.response_templates = self._load_response_templates()
        self.command_handlers = self._setup_command_handlers()
        self.logger.info("UserInteraction initialized")
    
    def _load_response_templates(self) -> Dict[str, str]:
        """
        Load response templates for different interaction types.
        
        Returns:
            Dict[str, str]: Dictionary of response templates
        """
        return {
            "greeting": "Hello! I'm here to help you with your questions. How can I assist you today?",
            "farewell": "Thank you for using the AI assistant. Have a great day!",
            "help": "I can help you with text analysis, answering questions, and general conversation. Try asking me something!",
            "error": "I'm sorry, I encountered an error processing your request. Please try again.",
            "unknown": "I'm not sure I understand. Could you please rephrase your question?",
            "positive_feedback": "I'm glad I could help! Is there anything else you'd like to know?",
            "negative_feedback": "I'm sorry to hear that. Let me try to help you better.",
            "analysis_complete": "I've completed the analysis. Here are the results:",
            "processing": "I'm processing your request. Please wait a moment...",
            "clarification": "Could you provide more details about what you're looking for?"
        }
    
    def _setup_command_handlers(self) -> Dict[str, Callable]:
        """
        Set up command handlers for different user commands.
        
        Returns:
            Dict[str, Callable]: Dictionary of command handlers
        """
        return {
            "analyze": self._handle_analyze_command,
            "help": self._handle_help_command,
            "status": self._handle_status_command,
            "history": self._handle_history_command,
            "clear": self._handle_clear_command,
            "sentiment": self._handle_sentiment_command,
            "keywords": self._handle_keywords_command,
            "summarize": self._handle_summarize_command,
            "stats": self._handle_stats_command
        }
    
    def process_user_input(self, user_input: str, user_id: str = "default") -> Dict[str, Any]:
        """
        Process user input and generate appropriate response.
        
        Args:
            user_input (str): User's input text
            user_id (str): Unique identifier for the user
            
        Returns:
            Dict[str, Any]: Response dictionary with text and metadata
        """
        if not self.validate_input(user_input, str):
            return self._create_response("I need some text to work with. Please provide your input.", "error")
        
        # Record the interaction
        interaction = {
            "user_id": user_id,
            "input": user_input,
            "timestamp": datetime.now().isoformat(),
            "input_analysis": self.text_processor.analyze_sentiment(user_input)
        }
        
        # Update user session
        if user_id not in self.user_sessions:
            self.user_sessions[user_id] = {
                "start_time": datetime.now().isoformat(),
                "interaction_count": 0
            }
        
        self.user_sessions[user_id]["interaction_count"] += 1
        
        # Process input
        response = self._generate_response(user_input, user_id)
        
        # Complete the interaction record
        interaction["response"] = response
        self.conversation_history.append(interaction)
        
        # Limit conversation history size
        if len(self.conversation_history) > 100:
            self.conversation_history = self.conversation_history[-100:]
        
        self.logger.info(f"Processed input from user {user_id}: {user_input[:50]}...")
        return response
    
    def _generate_response(self, user_input: str, user_id: str) -> Dict[str, Any]:
        """
        Generate response based on user input.
        
        Args:
            user_input (str): User's input text
            user_id (str): User identifier
            
        Returns:
            Dict[str, Any]: Generated response
        """
        # Clean and analyze input
        cleaned_input = self.text_processor.clean_text(user_input)
        tokens = self.text_processor.tokenize(cleaned_input, remove_stopwords=False)
        
        # Check for commands
        if tokens and tokens[0].startswith('/'):
            return self._handle_command(tokens[0][1:], ' '.join(tokens[1:]), user_id)
        
        # Check for greetings
        greeting_words = ['hello', 'hi', 'hey', 'greetings', 'good morning', 'good afternoon', 'good evening']
        if any(word in cleaned_input.lower() for word in greeting_words):
            return self._create_response(self.response_templates["greeting"], "greeting")
        
        # Check for farewells
        farewell_words = ['bye', 'goodbye', 'farewell', 'see you', 'thanks', 'thank you']
        if any(word in cleaned_input.lower() for word in farewell_words):
            return self._create_response(self.response_templates["farewell"], "farewell")
        
        # Check for help requests
        help_words = ['help', 'what can you do', 'how to', 'instructions']
        if any(word in cleaned_input.lower() for word in help_words):
            return self._create_response(self._generate_help_response(), "help")
        
        # Default response with basic analysis
        return self._create_analysis_response(user_input)
    
    def _handle_command(self, command: str, args: str, user_id: str) -> Dict[str, Any]:
        """
        Handle user commands.
        
        Args:
            command (str): Command name
            args (str): Command arguments
            user_id (str): User identifier
            
        Returns:
            Dict[str, Any]: Command response
        """
        if command in self.command_handlers:
            return self.command_handlers[command](args, user_id)
        else:
            return self._create_response(f"Unknown command: {command}. Type /help for available commands.", "error")
    
    def _handle_analyze_command(self, args: str, user_id: str) -> Dict[str, Any]:
        """Handle analyze command."""
        if not args.strip():
            return self._create_response("Please provide text to analyze after the /analyze command.", "error")
        return self._create_analysis_response(args)
    
    def _handle_help_command(self, args: str, user_id: str) -> Dict[str, Any]:
        """Handle help command."""
        return self._create_response(self._generate_help_response(), "help")
    
    def _handle_status_command(self, args: str, user_id: str) -> Dict[str, Any]:
        """Handle status command."""
        status = self.get_status()
        status["user_sessions"] = len(self.user_sessions)
        status["conversation_history"] = len(self.conversation_history)
        return self._create_response(f"System Status: {json.dumps(status, indent=2)}", "status")
    
    def _handle_history_command(self, args: str, user_id: str) -> Dict[str, Any]:
        """Handle history command."""
        user_history = [h for h in self.conversation_history if h["user_id"] == user_id]
        history_summary = f"You have {len(user_history)} interactions in history."
        if user_history:
            recent = user_history[-3:]  # Show last 3 interactions
            history_summary += "\n\nRecent interactions:"
            for i, interaction in enumerate(recent, 1):
                history_summary += f"\n{i}. Input: {interaction['input'][:50]}..."
        return self._create_response(history_summary, "history")
    
    def _handle_clear_command(self, args: str, user_id: str) -> Dict[str, Any]:
        """Handle clear command."""
        # Clear user's conversation history
        self.conversation_history = [h for h in self.conversation_history if h["user_id"] != user_id]
        if user_id in self.user_sessions:
            del self.user_sessions[user_id]
        return self._create_response("Your conversation history has been cleared.", "clear")
    
    def _handle_sentiment_command(self, args: str, user_id: str) -> Dict[str, Any]:
        """Handle sentiment analysis command."""
        if not args.strip():
            return self._create_response("Please provide text to analyze after the /sentiment command.", "error")
        
        sentiment_result = self.text_processor.analyze_sentiment(args)
        response_text = f"Sentiment Analysis Results:\n"
        response_text += f"Sentiment: {sentiment_result['sentiment'].upper()}\n"
        response_text += f"Confidence: {sentiment_result['confidence']:.2f}\n"
        response_text += f"Positive words: {sentiment_result['scores']['positive']}\n"
        response_text += f"Negative words: {sentiment_result['scores']['negative']}"
        
        return self._create_response(response_text, "sentiment", sentiment_result)
    
    def _handle_keywords_command(self, args: str, user_id: str) -> Dict[str, Any]:
        """Handle keyword extraction command."""
        if not args.strip():
            return self._create_response("Please provide text to analyze after the /keywords command.", "error")
        
        keywords = self.text_processor.extract_keywords(args, max_keywords=10)
        response_text = "Top Keywords:\n"
        for i, (keyword, frequency) in enumerate(keywords, 1):
            response_text += f"{i}. {keyword} ({frequency} times)\n"
        
        return self._create_response(response_text, "keywords", {"keywords": keywords})
    
    def _handle_summarize_command(self, args: str, user_id: str) -> Dict[str, Any]:
        """Handle text summarization command."""
        if not args.strip():
            return self._create_response("Please provide text to summarize after the /summarize command.", "error")
        
        summary = self.text_processor.summarize_text(args, max_sentences=3)
        response_text = f"Text Summary:\n{summary}"
        
        return self._create_response(response_text, "summarize", {"summary": summary})
    
    def _handle_stats_command(self, args: str, user_id: str) -> Dict[str, Any]:
        """Handle text statistics command."""
        if not args.strip():
            return self._create_response("Please provide text to analyze after the /stats command.", "error")
        
        stats = self.text_processor.count_words(args)
        response_text = "Text Statistics:\n"
        for key, value in stats.items():
            if isinstance(value, float):
                response_text += f"{key.replace('_', ' ').title()}: {value:.2f}\n"
            else:
                response_text += f"{key.replace('_', ' ').title()}: {value}\n"
        
        return self._create_response(response_text, "stats", stats)
    
    def _create_analysis_response(self, text: str) -> Dict[str, Any]:
        """
        Create a comprehensive analysis response.
        
        Args:
            text (str): Text to analyze
            
        Returns:
            Dict[str, Any]: Analysis response
        """
        # Perform various analyses
        sentiment = self.text_processor.analyze_sentiment(text)
        keywords = self.text_processor.extract_keywords(text, max_keywords=5)
        stats = self.text_processor.count_words(text)
        
        # Generate response text
        response_text = f"{self.response_templates['analysis_complete']}\n\n"
        response_text += f"Sentiment: {sentiment['sentiment'].upper()} (confidence: {sentiment['confidence']:.2f})\n"
        response_text += f"Word count: {stats['total_words']}\n"
        response_text += f"Unique words: {stats['unique_words']}\n"
        
        if keywords:
            response_text += f"Top keywords: {', '.join([kw[0] for kw in keywords[:3]])}\n"
        
        response_text += f"\nType /help to see available commands for more detailed analysis."
        
        return self._create_response(response_text, "analysis", {
            "sentiment": sentiment,
            "keywords": keywords,
            "stats": stats
        })
    
    def _generate_help_response(self) -> str:
        """Generate help response with available commands."""
        help_text = self.response_templates["help"] + "\n\n"
        help_text += "Available commands:\n"
        help_text += "/analyze <text> - Comprehensive text analysis\n"
        help_text += "/sentiment <text> - Sentiment analysis\n"
        help_text += "/keywords <text> - Extract keywords\n"
        help_text += "/summarize <text> - Summarize text\n"
        help_text += "/stats <text> - Text statistics\n"
        help_text += "/status - System status\n"
        help_text += "/history - Your conversation history\n"
        help_text += "/clear - Clear your conversation history\n"
        help_text += "/help - Show this help message"
        
        return help_text
    
    def _create_response(self, text: str, response_type: str, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Create a standardized response dictionary.
        
        Args:
            text (str): Response text
            response_type (str): Type of response
            data (Optional[Dict[str, Any]]): Additional data
            
        Returns:
            Dict[str, Any]: Formatted response
        """
        return {
            "text": text,
            "type": response_type,
            "timestamp": datetime.now().isoformat(),
            "data": data or {}
        }
    
    def get_conversation_history(self, user_id: str = None) -> List[Dict[str, Any]]:
        """
        Get conversation history for a user or all users.
        
        Args:
            user_id (str, optional): User ID to filter by
            
        Returns:
            List[Dict[str, Any]]: Conversation history
        """
        if user_id:
            return [h for h in self.conversation_history if h["user_id"] == user_id]
        return self.conversation_history
    
    def get_user_sessions(self) -> Dict[str, Dict[str, Any]]:
        """
        Get information about all user sessions.
        
        Returns:
            Dict[str, Dict[str, Any]]: User session information
        """
        return self.user_sessions