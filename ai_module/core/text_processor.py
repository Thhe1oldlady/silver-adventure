"""
Text processing capabilities for AI module.

This module provides text processing and analysis functionality including
natural language processing, sentiment analysis, and text manipulation.
"""

import re
from typing import Dict, List, Any, Optional, Tuple
from collections import Counter
from .ai_base import AIBase


class TextProcessor(AIBase):
    """
    Text processing class providing NLP and text analysis capabilities.
    
    This class extends AIBase to provide specialized text processing functions
    including tokenization, sentiment analysis, keyword extraction, and more.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the TextProcessor.
        
        Args:
            config (Optional[Dict[str, Any]]): Configuration dictionary
        """
        super().__init__(config)
        self.stopwords = self._load_stopwords()
        self.sentiment_keywords = self._load_sentiment_keywords()
        self.logger.info("TextProcessor initialized")
    
    def _load_stopwords(self) -> set:
        """
        Load common English stopwords.
        
        Returns:
            set: Set of stopwords
        """
        return {
            'a', 'an', 'and', 'are', 'as', 'at', 'be', 'by', 'for', 'from',
            'has', 'he', 'in', 'is', 'it', 'its', 'of', 'on', 'that', 'the',
            'to', 'was', 'were', 'will', 'with', 'the', 'this', 'but', 'they',
            'have', 'had', 'what', 'said', 'each', 'which', 'their', 'time',
            'will', 'about', 'if', 'up', 'out', 'many', 'then', 'them', 'these',
            'so', 'some', 'her', 'would', 'make', 'like', 'into', 'him', 'has',
            'two', 'more', 'go', 'no', 'way', 'could', 'my', 'than', 'first',
            'been', 'call', 'who', 'oil', 'sit', 'now', 'find', 'down', 'day',
            'did', 'get', 'come', 'made', 'may', 'part'
        }
    
    def _load_sentiment_keywords(self) -> Dict[str, List[str]]:
        """
        Load sentiment analysis keywords.
        
        Returns:
            Dict[str, List[str]]: Dictionary of positive and negative keywords
        """
        return {
            'positive': [
                'good', 'great', 'excellent', 'amazing', 'wonderful', 'fantastic',
                'awesome', 'brilliant', 'perfect', 'love', 'like', 'enjoy',
                'happy', 'pleased', 'satisfied', 'delighted', 'thrilled'
            ],
            'negative': [
                'bad', 'terrible', 'awful', 'horrible', 'disgusting', 'hate',
                'dislike', 'disappointed', 'frustrated', 'angry', 'upset',
                'annoyed', 'sad', 'unhappy', 'dissatisfied', 'poor', 'worst'
            ]
        }
    
    def tokenize(self, text: str, remove_stopwords: bool = True) -> List[str]:
        """
        Tokenize text into individual words.
        
        Args:
            text (str): Text to tokenize
            remove_stopwords (bool): Whether to remove stopwords
            
        Returns:
            List[str]: List of tokens
        """
        if not self.validate_input(text, str):
            return []
        
        # Convert to lowercase and remove punctuation
        text = re.sub(r'[^\w\s]', '', text.lower())
        tokens = text.split()
        
        if remove_stopwords:
            tokens = [token for token in tokens if token not in self.stopwords]
        
        self.logger.debug(f"Tokenized text into {len(tokens)} tokens")
        return tokens
    
    def analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """
        Perform basic sentiment analysis on text.
        
        Args:
            text (str): Text to analyze
            
        Returns:
            Dict[str, Any]: Sentiment analysis results
        """
        if not self.validate_input(text, str):
            return {"sentiment": "neutral", "confidence": 0.0, "scores": {}}
        
        tokens = self.tokenize(text, remove_stopwords=False)
        
        positive_count = sum(1 for token in tokens if token in self.sentiment_keywords['positive'])
        negative_count = sum(1 for token in tokens if token in self.sentiment_keywords['negative'])
        total_sentiment_words = positive_count + negative_count
        
        if total_sentiment_words == 0:
            sentiment = "neutral"
            confidence = 0.0
        elif positive_count > negative_count:
            sentiment = "positive"
            confidence = positive_count / total_sentiment_words
        elif negative_count > positive_count:
            sentiment = "negative"
            confidence = negative_count / total_sentiment_words
        else:
            sentiment = "neutral"
            confidence = 0.5
        
        result = {
            "sentiment": sentiment,
            "confidence": confidence,
            "scores": {
                "positive": positive_count,
                "negative": negative_count,
                "total_words": len(tokens)
            }
        }
        
        self.logger.debug(f"Sentiment analysis: {sentiment} (confidence: {confidence:.2f})")
        return result
    
    def extract_keywords(self, text: str, max_keywords: int = 10) -> List[Tuple[str, int]]:
        """
        Extract keywords from text based on frequency.
        
        Args:
            text (str): Text to extract keywords from
            max_keywords (int): Maximum number of keywords to return
            
        Returns:
            List[Tuple[str, int]]: List of (keyword, frequency) tuples
        """
        if not self.validate_input(text, str):
            return []
        
        tokens = self.tokenize(text, remove_stopwords=True)
        
        # Filter tokens by length (avoid very short words)
        filtered_tokens = [token for token in tokens if len(token) > 2]
        
        # Count frequency
        word_freq = Counter(filtered_tokens)
        
        # Get top keywords
        keywords = word_freq.most_common(max_keywords)
        
        self.logger.debug(f"Extracted {len(keywords)} keywords from text")
        return keywords
    
    def summarize_text(self, text: str, max_sentences: int = 3) -> str:
        """
        Create a basic summary of text by extracting key sentences.
        
        Args:
            text (str): Text to summarize
            max_sentences (int): Maximum number of sentences in summary
            
        Returns:
            str: Summary text
        """
        if not self.validate_input(text, str):
            return ""
        
        # Split into sentences
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        if len(sentences) <= max_sentences:
            return text
        
        # Simple scoring based on sentence length and keyword frequency
        keywords = dict(self.extract_keywords(text, max_keywords=20))
        
        sentence_scores = []
        for sentence in sentences:
            score = 0
            tokens = self.tokenize(sentence, remove_stopwords=True)
            for token in tokens:
                if token in keywords:
                    score += keywords[token]
            sentence_scores.append((sentence, score))
        
        # Sort by score and take top sentences
        sentence_scores.sort(key=lambda x: x[1], reverse=True)
        top_sentences = sentence_scores[:max_sentences]
        
        # Maintain original order
        summary_sentences = []
        for sentence in sentences:
            if any(sentence == s[0] for s in top_sentences):
                summary_sentences.append(sentence)
                if len(summary_sentences) >= max_sentences:
                    break
        
        summary = '. '.join(summary_sentences) + '.'
        self.logger.debug(f"Created summary with {len(summary_sentences)} sentences")
        return summary
    
    def count_words(self, text: str) -> Dict[str, int]:
        """
        Count various text statistics.
        
        Args:
            text (str): Text to analyze
            
        Returns:
            Dict[str, int]: Dictionary with word counts and statistics
        """
        if not self.validate_input(text, str):
            return {}
        
        tokens = self.tokenize(text, remove_stopwords=False)
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        stats = {
            "total_words": len(tokens),
            "unique_words": len(set(tokens)),
            "sentences": len(sentences),
            "characters": len(text),
            "characters_no_spaces": len(text.replace(' ', '')),
            "average_word_length": sum(len(word) for word in tokens) / len(tokens) if tokens else 0,
            "average_sentence_length": len(tokens) / len(sentences) if sentences else 0
        }
        
        self.logger.debug(f"Text statistics calculated: {stats}")
        return stats
    
    def clean_text(self, text: str, remove_extra_spaces: bool = True, 
                   remove_special_chars: bool = False) -> str:
        """
        Clean and normalize text.
        
        Args:
            text (str): Text to clean
            remove_extra_spaces (bool): Whether to remove extra spaces
            remove_special_chars (bool): Whether to remove special characters
            
        Returns:
            str: Cleaned text
        """
        if not self.validate_input(text, str):
            return ""
        
        cleaned = text
        
        if remove_extra_spaces:
            cleaned = re.sub(r'\s+', ' ', cleaned).strip()
        
        if remove_special_chars:
            cleaned = re.sub(r'[^\w\s]', '', cleaned)
        
        self.logger.debug("Text cleaned and normalized")
        return cleaned