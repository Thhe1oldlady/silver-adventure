"""
Helper utilities for AI module.

This module provides various helper functions and utilities that are
commonly used across the AI module components.
"""

import re
import uuid
import hashlib
import time
from typing import Any, Dict, List, Optional, Union, Callable
from datetime import datetime, timedelta
from pathlib import Path
import json


class Helper:
    """
    Helper class providing utility functions for AI module.
    
    This class contains static methods that provide common functionality
    such as string manipulation, data validation, file operations, and more.
    """
    
    @staticmethod
    def generate_id(prefix: str = "ai", length: int = 8) -> str:
        """
        Generate a unique identifier.
        
        Args:
            prefix (str): Prefix for the ID
            length (int): Length of the random part
            
        Returns:
            str: Generated unique ID
        """
        unique_part = str(uuid.uuid4())[:length]
        return f"{prefix}_{unique_part}"
    
    @staticmethod
    def hash_text(text: str, algorithm: str = "sha256") -> str:
        """
        Generate hash of text.
        
        Args:
            text (str): Text to hash
            algorithm (str): Hash algorithm to use
            
        Returns:
            str: Hash of the text
        """
        if algorithm == "sha256":
            return hashlib.sha256(text.encode()).hexdigest()
        elif algorithm == "md5":
            return hashlib.md5(text.encode()).hexdigest()
        else:
            raise ValueError(f"Unsupported hash algorithm: {algorithm}")
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """
        Validate email address format.
        
        Args:
            email (str): Email address to validate
            
        Returns:
            bool: True if valid, False otherwise
        """
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    @staticmethod
    def validate_url(url: str) -> bool:
        """
        Validate URL format.
        
        Args:
            url (str): URL to validate
            
        Returns:
            bool: True if valid, False otherwise
        """
        pattern = r'^https?://'
        return re.match(pattern, url) is not None
    
    @staticmethod
    def clean_filename(filename: str) -> str:
        """
        Clean filename by removing invalid characters.
        
        Args:
            filename (str): Filename to clean
            
        Returns:
            str: Cleaned filename
        """
        # Remove invalid characters
        cleaned = re.sub(r'[<>:"/\\|?*]', '', filename)
        # Replace spaces with underscores
        cleaned = cleaned.replace(' ', '_')
        # Remove multiple underscores
        cleaned = re.sub(r'_+', '_', cleaned)
        # Remove leading/trailing underscores
        cleaned = cleaned.strip('_')
        
        return cleaned or "unnamed_file"
    
    @staticmethod
    def truncate_text(text: str, max_length: int, suffix: str = "...") -> str:
        """
        Truncate text to specified length.
        
        Args:
            text (str): Text to truncate
            max_length (int): Maximum length
            suffix (str): Suffix to add if truncated
            
        Returns:
            str: Truncated text
        """
        if len(text) <= max_length:
            return text
        
        return text[:max_length - len(suffix)] + suffix
    
    @staticmethod
    def format_duration(seconds: float) -> str:
        """
        Format duration in seconds to human-readable format.
        
        Args:
            seconds (float): Duration in seconds
            
        Returns:
            str: Formatted duration
        """
        if seconds < 60:
            return f"{seconds:.1f} seconds"
        elif seconds < 3600:
            minutes = seconds / 60
            return f"{minutes:.1f} minutes"
        elif seconds < 86400:
            hours = seconds / 3600
            return f"{hours:.1f} hours"
        else:
            days = seconds / 86400
            return f"{days:.1f} days"
    
    @staticmethod
    def format_timestamp(timestamp: Optional[datetime] = None, format_str: str = "%Y-%m-%d %H:%M:%S") -> str:
        """
        Format timestamp to string.
        
        Args:
            timestamp (Optional[datetime]): Timestamp to format (defaults to now)
            format_str (str): Format string
            
        Returns:
            str: Formatted timestamp
        """
        if timestamp is None:
            timestamp = datetime.now()
        
        return timestamp.strftime(format_str)
    
    @staticmethod
    def parse_timestamp(timestamp_str: str, format_str: str = "%Y-%m-%d %H:%M:%S") -> datetime:
        """
        Parse timestamp string to datetime object.
        
        Args:
            timestamp_str (str): Timestamp string
            format_str (str): Format string
            
        Returns:
            datetime: Parsed datetime object
        """
        return datetime.strptime(timestamp_str, format_str)
    
    @staticmethod
    def safe_get(dictionary: Dict[str, Any], key: str, default: Any = None) -> Any:
        """
        Safely get value from dictionary with nested key support.
        
        Args:
            dictionary (Dict[str, Any]): Dictionary to get value from
            key (str): Key (supports dot notation)
            default (Any): Default value if key not found
            
        Returns:
            Any: Value or default
        """
        keys = key.split('.')
        value = dictionary
        
        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default
    
    @staticmethod
    def flatten_dict(dictionary: Dict[str, Any], separator: str = ".") -> Dict[str, Any]:
        """
        Flatten nested dictionary.
        
        Args:
            dictionary (Dict[str, Any]): Dictionary to flatten
            separator (str): Separator for nested keys
            
        Returns:
            Dict[str, Any]: Flattened dictionary
        """
        def _flatten(obj, parent_key=""):
            items = []
            if isinstance(obj, dict):
                for key, value in obj.items():
                    new_key = f"{parent_key}{separator}{key}" if parent_key else key
                    items.extend(_flatten(value, new_key).items())
            else:
                return {parent_key: obj}
            return dict(items)
        
        return _flatten(dictionary)
    
    @staticmethod
    def merge_dicts(*dicts: Dict[str, Any]) -> Dict[str, Any]:
        """
        Merge multiple dictionaries.
        
        Args:
            *dicts: Dictionaries to merge
            
        Returns:
            Dict[str, Any]: Merged dictionary
        """
        result = {}
        for d in dicts:
            result.update(d)
        return result
    
    @staticmethod
    def retry_operation(
        operation: Callable, 
        max_attempts: int = 3, 
        delay: float = 1.0, 
        backoff_factor: float = 2.0
    ) -> Any:
        """
        Retry an operation with exponential backoff.
        
        Args:
            operation (Callable): Operation to retry
            max_attempts (int): Maximum number of attempts
            delay (float): Initial delay between attempts
            backoff_factor (float): Factor to multiply delay by after each attempt
            
        Returns:
            Any: Result of the operation
            
        Raises:
            Exception: Last exception if all attempts fail
        """
        last_exception = None
        
        for attempt in range(max_attempts):
            try:
                return operation()
            except Exception as e:
                last_exception = e
                if attempt < max_attempts - 1:
                    time.sleep(delay)
                    delay *= backoff_factor
        
        raise last_exception
    
    @staticmethod
    def chunk_list(lst: List[Any], chunk_size: int) -> List[List[Any]]:
        """
        Split list into chunks of specified size.
        
        Args:
            lst (List[Any]): List to chunk
            chunk_size (int): Size of each chunk
            
        Returns:
            List[List[Any]]: List of chunks
        """
        return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]
    
    @staticmethod
    def file_exists(file_path: Union[str, Path]) -> bool:
        """
        Check if file exists.
        
        Args:
            file_path (Union[str, Path]): Path to file
            
        Returns:
            bool: True if file exists, False otherwise
        """
        return Path(file_path).exists()
    
    @staticmethod
    def create_directory(dir_path: Union[str, Path]) -> None:
        """
        Create directory if it doesn't exist.
        
        Args:
            dir_path (Union[str, Path]): Path to directory
        """
        Path(dir_path).mkdir(parents=True, exist_ok=True)
    
    @staticmethod
    def read_json_file(file_path: Union[str, Path]) -> Dict[str, Any]:
        """
        Read JSON file.
        
        Args:
            file_path (Union[str, Path]): Path to JSON file
            
        Returns:
            Dict[str, Any]: Parsed JSON data
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    @staticmethod
    def write_json_file(file_path: Union[str, Path], data: Dict[str, Any]) -> None:
        """
        Write data to JSON file.
        
        Args:
            file_path (Union[str, Path]): Path to JSON file
            data (Dict[str, Any]): Data to write
        """
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    @staticmethod
    def get_file_size(file_path: Union[str, Path]) -> int:
        """
        Get file size in bytes.
        
        Args:
            file_path (Union[str, Path]): Path to file
            
        Returns:
            int: File size in bytes
        """
        return Path(file_path).stat().st_size
    
    @staticmethod
    def format_file_size(size_bytes: int) -> str:
        """
        Format file size in human-readable format.
        
        Args:
            size_bytes (int): Size in bytes
            
        Returns:
            str: Formatted size
        """
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024 ** 2:
            return f"{size_bytes / 1024:.1f} KB"
        elif size_bytes < 1024 ** 3:
            return f"{size_bytes / (1024 ** 2):.1f} MB"
        else:
            return f"{size_bytes / (1024 ** 3):.1f} GB"
    
    @staticmethod
    def sanitize_input(text: str) -> str:
        """
        Sanitize user input by removing potentially dangerous characters.
        
        Args:
            text (str): Input text to sanitize
            
        Returns:
            str: Sanitized text
        """
        # Remove HTML tags
        text = re.sub(r'<[^>]+>', '', text)
        # Remove script tags and content
        text = re.sub(r'<script.*?</script>', '', text, flags=re.IGNORECASE | re.DOTALL)
        # Remove potentially dangerous characters
        text = re.sub(r'[<>"\']', '', text)
        
        return text.strip()
    
    @staticmethod
    def normalize_text(text: str) -> str:
        """
        Normalize text by removing extra whitespace and converting to lowercase.
        
        Args:
            text (str): Text to normalize
            
        Returns:
            str: Normalized text
        """
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        # Convert to lowercase
        text = text.lower()
        # Strip leading/trailing whitespace
        text = text.strip()
        
        return text
    
    @staticmethod
    def calculate_similarity(text1: str, text2: str) -> float:
        """
        Calculate simple similarity between two texts using Jaccard similarity.
        
        Args:
            text1 (str): First text
            text2 (str): Second text
            
        Returns:
            float: Similarity score between 0 and 1
        """
        # Normalize texts
        text1 = Helper.normalize_text(text1)
        text2 = Helper.normalize_text(text2)
        
        # Split into words
        words1 = set(text1.split())
        words2 = set(text2.split())
        
        # Calculate Jaccard similarity
        intersection = len(words1 & words2)
        union = len(words1 | words2)
        
        return intersection / union if union > 0 else 0.0