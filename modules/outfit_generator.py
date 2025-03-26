#!/usr/bin/env python3
"""
Outfit Generator for the Clothing Database System.
This module provides logic for generating outfit suggestions based on clothing items.
"""

import random
from db.db_operations import DatabaseManager

class OutfitGenerator:
    """Class to generate outfit suggestions based on clothing items in the database."""
    
    def __init__(self, db_manager=None):
        """Initialize the outfit generator with a database manager."""
        self.db = db_manager if db_manager else DatabaseManager()
    
    def generate_outfit(self, style=None, occasion=None, season=None):
        """
        Generate an outfit based on optional style, occasion, and season parameters.
        
        Args:
            style (str, optional): Style preference (e.g., 'Casual', 'Formal')
            occasion (str, optional): Occasion for the outfit (e.g., 'Work', 'Date Night')
            season (str, optional): Season for the outfit (e.g., 'Summer', 'Winter')
            
        Returns:
            dict: Generated outfit data including name, items, and metadata
        """
        # Get all clothing items
        items = self.db.get_all_clothing_items()
        if not items:
            return {
                'success': False,
                'message': "No clothing items found in the database. Please add some items first."
            }
        
        # Filter items by season if specified
        if season:
            season_items = [item for item in items if item['season'] and 
                           (season.lower() in item['season'].lower() or 
                            "all-season" in item['season'].lower())]
            if season_items:
                items = season_items
        
        # Filter items by occasion if specified
        if occasion:
            occasion_items = [item for item in items if item['occasion'] and 
                             occasion.lower() in item['occasion'].lower()]
            if occasion_items:
                items = occasion_items
        
        # Group items by type
        items_by_type = {}
        for item in items:
            item_type = item['type']
            if item_type not in items_by_type:
                items_by_type[item_type] = []
            items_by_type[item_type].append(item)
        
        # Define essential item types based on style
        essential_types = self._get_essential_types(style)
        
        # Create an outfit with essential items
        outfit_items = []
        outfit_description = []
        
        # Try to add items for each essential type
        for type_group in essential_types:
            added = False
            for item_type in type_group:
                if item_type in items_by_type and items_by_type[item_type]:
                    # Select an item of this type
                    item = random.choice(items_by_type[item_type])
                    outfit_items.append(item)
                    outfit_description.append(f"{item['name']} ({item['color']})")
                    added = True
                    break
            
            # If we couldn't add any item from this type group, log it
            if not added and type_group:
                print(f"Warning: Could not find any items of types: {', '.join(type_group)}")
        
        # Try to add accessories if available
        accessory_types = ['Accessory', 'Jewelry', 'Hat', 'Scarf', 'Belt']
        for acc_type in accessory_types:
            if acc_type in items_by_type and items_by_type[acc_type] and random.random() < 0.7:  # 70% chance to add accessory
                accessory = random.choice(items_by_type[acc_type])
                outfit_items.append(accessory)
                outfit_description.append(f"{accessory['name']} ({accessory['color']})")
        
        # Generate outfit name
        outfit_name = self._generate_outfit_name(style, occasion, season)
        
        # For testing purposes, allow outfits with any number of items
        # In a real application, we might want to enforce a minimum number of items
        if len(outfit_items) == 0:
            return {
                'success': False,
                'message': "Could not create an outfit with your current clothing items. Please add more items to your database."
            }
        
        # Create response
        response_message = f"I've created a {outfit_name.lower()} for you with:\n"
        for desc in outfit_description:
            response_message += f"- {desc}\n"
        
        if style or occasion or season:
            response_message += "\nThis outfit is suitable for "
            if style:
                response_message += f"a {style.lower()} style"
                if occasion or season:
                    response_message += ", "
            if occasion:
                response_message += f"{occasion.lower()}"
                if season:
                    response_message += ", "
            if season:
                response_message += f"during {season.lower()}"
            response_message += "."
        
        response_message += "\n\nYou can save this outfit or generate a new one."
        
        # Prepare outfit data for saving
        outfit_data = {
            'name': outfit_name,
            'items': [{'item_id': item['item_id'], 'name': item['name'], 'type': item['type'], 'color': item['color']} 
                     for item in outfit_items],
            'style': style,
            'occasion': occasion,
            'season': season
        }
        
        return {
            'success': True,
            'message': response_message,
            'outfit': outfit_data
        }
    
    def _get_essential_types(self, style=None):
        """
        Get essential item types based on style.
        
        Args:
            style (str, optional): Style preference
            
        Returns:
            list: List of item type groups, where each group contains alternative types
        """
        # Default essential types (casual)
        essential_types = [
            ['Shirt', 'T-shirt', 'Blouse', 'Top'],  # Upper body
            ['Pants', 'Jeans', 'Shorts', 'Skirt'],  # Lower body
            ['Shoes', 'Sneakers', 'Sandals', 'Boots']  # Footwear
        ]
        
        # Adjust based on style
        if style:
            style = style.lower()
            
            if 'formal' in style:
                essential_types = [
                    ['Dress Shirt', 'Blouse', 'Shirt'],
                    ['Dress Pants', 'Skirt', 'Suit Pants'],
                    ['Dress Shoes', 'Heels'],
                    ['Jacket', 'Blazer', 'Suit Jacket']
                ]
            elif 'business' in style:
                essential_types = [
                    ['Dress Shirt', 'Blouse', 'Shirt'],
                    ['Dress Pants', 'Skirt', 'Suit Pants'],
                    ['Dress Shoes', 'Heels', 'Loafers'],
                    ['Blazer', 'Jacket']
                ]
            elif 'casual' in style:
                # Already set as default
                pass
            elif 'sporty' in style or 'athletic' in style:
                essential_types = [
                    ['T-shirt', 'Tank Top', 'Sports Bra'],
                    ['Shorts', 'Leggings', 'Track Pants'],
                    ['Sneakers', 'Athletic Shoes'],
                ]
            elif 'bohemian' in style or 'boho' in style:
                essential_types = [
                    ['Blouse', 'Tunic', 'Top'],
                    ['Maxi Skirt', 'Flowy Pants', 'Jeans'],
                    ['Sandals', 'Boots', 'Flats'],
                ]
            elif 'vintage' in style or 'retro' in style:
                essential_types = [
                    ['Blouse', 'Shirt', 'Top'],
                    ['High-Waisted Pants', 'Skirt', 'Jeans'],
                    ['Loafers', 'Heels', 'Boots'],
                ]
            elif 'minimalist' in style:
                essential_types = [
                    ['Shirt', 'T-shirt', 'Blouse'],
                    ['Pants', 'Skirt', 'Jeans'],
                    ['Sneakers', 'Flats', 'Boots'],
                ]
        
        return essential_types
    
    def _generate_outfit_name(self, style=None, occasion=None, season=None):
        """
        Generate a name for the outfit based on style, occasion, and season.
        
        Args:
            style (str, optional): Style preference
            occasion (str, optional): Occasion for the outfit
            season (str, optional): Season for the outfit
            
        Returns:
            str: Generated outfit name
        """
        name_parts = []
        
        if style:
            name_parts.append(style)
        
        if occasion:
            name_parts.append(occasion)
        
        if season:
            name_parts.append(season)
        
        if not name_parts:
            name_parts.append("Everyday")
        
        name_parts.append("Outfit")
        
        return " ".join(name_parts)
    
    def generate_outfit_from_message(self, message):
        """
        Parse a natural language message to extract style, occasion, and season,
        then generate an outfit based on these parameters.
        
        Args:
            message (str): Natural language message requesting an outfit
            
        Returns:
            dict: Generated outfit data including name, items, and metadata
        """
        message = message.lower()
        
        # Extract style from message
        style = None
        style_keywords = {
            "casual": "Casual",
            "formal": "Formal",
            "business": "Business",
            "professional": "Business",
            "bohemian": "Bohemian",
            "boho": "Bohemian",
            "minimalist": "Minimalist",
            "vintage": "Vintage",
            "retro": "Vintage",
            "sporty": "Sporty",
            "athletic": "Sporty"
        }
        
        for keyword, style_name in style_keywords.items():
            if keyword in message:
                style = style_name
                break
        
        # Extract occasion from message
        occasion = None
        occasion_keywords = {
            "work": "Work",
            "office": "Work",
            "date": "Date Night",
            "party": "Party",
            "weekend": "Weekend",
            "casual": "Casual Outing",
            "vacation": "Vacation",
            "travel": "Travel",
            "interview": "Interview",
            "meeting": "Meeting",
            "special": "Special Occasion",
            "wedding": "Wedding",
            "dinner": "Dinner"
        }
        
        for keyword, occasion_name in occasion_keywords.items():
            if keyword in message:
                occasion = occasion_name
                break
        
        # Extract season from message
        season = None
        season_keywords = {
            "summer": "Summer",
            "winter": "Winter",
            "fall": "Fall",
            "autumn": "Fall",
            "spring": "Spring",
            "hot": "Summer",
            "cold": "Winter",
            "warm": "Summer",
            "cool": "Fall",
            "rainy": "Spring"
        }
        
        for keyword, season_name in season_keywords.items():
            if keyword in message:
                season = season_name
                break
        
        # Generate the outfit
        return self.generate_outfit(style, occasion, season)


# Example usage
if __name__ == "__main__":
    generator = OutfitGenerator()
    
    # Test with different parameters
    print("Casual Summer Outfit:")
    result = generator.generate_outfit("Casual", None, "Summer")
    print(result['message'] if result['success'] else result['message'])
    
    print("\nFormal Work Outfit:")
    result = generator.generate_outfit("Formal", "Work", None)
    print(result['message'] if result['success'] else result['message'])
    
    print("\nFrom message: 'I need something casual for a weekend outing'")
    result = generator.generate_outfit_from_message("I need something casual for a weekend outing")
    print(result['message'] if result['success'] else result['message'])
