#!/usr/bin/env python3
"""
Additional route for generating new outfits through the chatbot.
This adds a "generate new" functionality to the chatbot interface.
"""

from flask import jsonify

def add_generate_new_route(app, chatbot_var_name='chatbot'):
    """
    Add a route for generating new outfits to a Flask application.
    
    Args:
        app: Flask application instance
        chatbot_var_name: Name of the global chatbot variable
    """
    
    @app.route('/chatbot/generate_new', methods=['POST'])
    def generate_new_outfit():
        """Generate a new random outfit suggestion."""
        # Access the global chatbot instance
        if chatbot_var_name not in globals():
            return jsonify({
                'success': False, 
                'message': 'No active chatbot session. Please refresh the page and try again.'
            })
        
        # Get the chatbot instance
        chatbot_instance = globals()[chatbot_var_name]
        
        # Generate a new outfit
        result = chatbot_instance.generate_new_outfit()
        
        return jsonify(result)
    
    return generate_new_outfit
