#!/usr/bin/env python3
"""
Chatbot module for the Clothing Database System.
This module provides the chatbot functionality for interactive outfit suggestions.
"""

import re
import random
from modules.outfit_generator import OutfitGenerator

class OutfitChatbot:
    """Class to handle chatbot interactions for outfit suggestions."""
    
    def __init__(self, db_manager=None):
        """Initialize the chatbot with a database manager."""
        self.outfit_generator = OutfitGenerator(db_manager)
        self.conversation_history = []
        self.current_outfit = None
    
    def process_message(self, message):
        """
        Process a user message and generate a response.
        
        Args:
            message (str): User message
            
        Returns:
            dict: Response containing message text and any generated outfit
        """
        # Add user message to conversation history
        self.conversation_history.append({"role": "user", "content": message})
        
        # Check for special commands
        if self._is_greeting(message):
            return self._handle_greeting()
        
        if self._is_help_request(message):
            return self._handle_help_request()
        
        if self._is_feedback(message):
            return self._handle_feedback(message)
        
        # Default behavior: generate outfit suggestion
        result = self.outfit_generator.generate_outfit_from_message(message)
        
        # Store the current outfit if successful
        if result['success']:
            self.current_outfit = result['outfit']
        
        # Add assistant response to conversation history
        self.conversation_history.append({"role": "assistant", "content": result['message']})
        
        return result
    
    def save_current_outfit(self):
        """
        Prepare the current outfit for saving.
        
        Returns:
            dict: Current outfit data or error message
        """
        if not self.current_outfit:
            return {
                'success': False,
                'message': "No outfit has been generated yet. Ask for an outfit suggestion first."
            }
        
        return {
            'success': True,
            'message': f"Outfit '{self.current_outfit['name']}' ready to save!",
            'outfit': self.current_outfit
        }
    
    def generate_new_outfit(self):
        """
        Generate a new random outfit suggestion.
        
        Returns:
            dict: Generated outfit data
        """
        # Generate a random prompt
        prompts = [
            "I need a casual outfit",
            "Suggest a formal outfit",
            "What should I wear for work?",
            "I need something for the weekend",
            "Suggest a summer outfit",
            "What would look good for winter?",
            "I need a business casual look",
            "Suggest something for a date night"
        ]
        random_prompt = random.choice(prompts)
        
        # Process the random prompt
        result = self.process_message(random_prompt)
        
        # Add context to the response
        if result['success']:
            result['message'] = f"I've generated a new random outfit based on: '{random_prompt}'\n\n{result['message']}"
        
        return result
    
    def get_conversation_history(self, max_entries=10):
        """
        Get recent conversation history.
        
        Args:
            max_entries (int): Maximum number of conversation entries to return
            
        Returns:
            list: Recent conversation history
        """
        return self.conversation_history[-max_entries:] if self.conversation_history else []
    
    def _is_greeting(self, message):
        """Check if the message is a greeting."""
        greetings = ['hello', 'hi', 'hey', 'greetings', 'howdy', 'hola']
        message = message.lower()
        
        return any(greeting in message.split() for greeting in greetings)
    
    def _handle_greeting(self):
        """Handle a greeting message."""
        greetings = [
            "Hello! I'm your Outfit Assistant. How can I help you today?",
            "Hi there! Ready to find the perfect outfit?",
            "Hey! I can suggest outfits based on your clothing items. What are you looking for?",
            "Greetings! Tell me what kind of outfit you need, and I'll help you create it."
        ]
        
        response = random.choice(greetings)
        
        # Add assistant response to conversation history
        self.conversation_history.append({"role": "assistant", "content": response})
        
        return {
            'success': True,
            'message': response
        }
    
    def _is_help_request(self, message):
        """Check if the message is a help request."""
        help_phrases = ['help', 'how does this work', 'what can you do', 'instructions', 'guide me']
        message = message.lower()
        
        return any(phrase in message for phrase in help_phrases)
    
    def _handle_help_request(self):
        """Handle a help request message."""
        help_text = """
I'm your Outfit Assistant! Here's how I can help you:

1. Ask me to suggest an outfit, like:
   - "Suggest a casual outfit for summer"
   - "What should I wear to work tomorrow?"
   - "I need something formal for a dinner"

2. You can specify:
   - Style (casual, formal, business, bohemian, etc.)
   - Occasion (work, date, weekend, party, etc.)
   - Season (summer, winter, fall, spring)

3. After I suggest an outfit, you can:
   - Save it to your database
   - Ask for a different suggestion
   - Refine your request with more details

What kind of outfit would you like me to suggest?
"""
        
        # Add assistant response to conversation history
        self.conversation_history.append({"role": "assistant", "content": help_text})
        
        return {
            'success': True,
            'message': help_text
        }
    
    def _is_feedback(self, message):
        """Check if the message contains feedback about an outfit."""
        feedback_phrases = ['like it', 'don\'t like', 'love it', 'hate it', 'not what i want', 'perfect', 'good job', 'try again']
        message = message.lower()
        
        return any(phrase in message for phrase in feedback_phrases)
    
    def _handle_feedback(self, message):
        """Handle feedback about an outfit."""
        message = message.lower()
        
        if any(phrase in message for phrase in ['like it', 'love it', 'perfect', 'good job']):
            response = "I'm glad you like the outfit! Would you like to save it to your database?"
        else:
            response = "I'm sorry the outfit didn't meet your expectations. Let me try again with a different suggestion."
            # Generate a new outfit
            return self.generate_new_outfit()
        
        # Add assistant response to conversation history
        self.conversation_history.append({"role": "assistant", "content": response})
        
        return {
            'success': True,
            'message': response
        }


# Example usage
if __name__ == "__main__":
    chatbot = OutfitChatbot()
    
    # Test with different messages
    print("User: Hello")
    result = chatbot.process_message("Hello")
    print(f"Assistant: {result['message']}")
    
    print("\nUser: Can you help me find an outfit?")
    result = chatbot.process_message("Can you help me find an outfit?")
    print(f"Assistant: {result['message']}")
    
    print("\nUser: I need a casual outfit for summer")
    result = chatbot.process_message("I need a casual outfit for summer")
    print(f"Assistant: {result['message']}")
    
    print("\nUser: I like it!")
    result = chatbot.process_message("I like it!")
    print(f"Assistant: {result['message']}")
