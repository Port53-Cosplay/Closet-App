#!/usr/bin/env python3
"""
Color Palette Analysis module for the Clothing Database System.
This module provides functionality to analyze color palettes and personal color seasons.
"""

import json
from db.db_operations import DatabaseManager

class ColorPaletteAnalyzer:
    """Class to analyze color palettes and personal color seasons."""
    
    # Define color seasons and their characteristics
    COLOR_SEASONS = {
        'Winter': {
            'description': 'Clear, cool, and high-contrast colors',
            'best_colors': ['Black', 'White', 'Navy', 'Royal Blue', 'Ice Blue', 'Purple', 'Magenta', 'Red', 'Emerald Green'],
            'avoid_colors': ['Orange', 'Warm Brown', 'Gold', 'Olive Green', 'Beige', 'Ivory'],
            'characteristics': 'High contrast between skin, hair, and eyes. Often has cool undertones.'
        },
        'Summer': {
            'description': 'Soft, cool, and muted colors',
            'best_colors': ['Lavender', 'Mauve', 'Powder Blue', 'Slate Blue', 'Rose Pink', 'Soft Fuchsia', 'Periwinkle', 'Sage Green'],
            'avoid_colors': ['Black', 'Orange', 'Bright Yellow', 'Tomato Red', 'Bright Gold'],
            'characteristics': 'Low to medium contrast between skin, hair, and eyes. Cool undertones with soft appearance.'
        },
        'Spring': {
            'description': 'Warm, clear, and bright colors',
            'best_colors': ['Peach', 'Coral', 'Golden Yellow', 'Warm Green', 'Aqua', 'Light Turquoise', 'Ivory', 'Camel'],
            'avoid_colors': ['Black', 'Navy', 'Burgundy', 'Gray', 'Plum'],
            'characteristics': 'Low to medium contrast with warm, golden undertones. Often has golden highlights in hair.'
        },
        'Autumn': {
            'description': 'Warm, muted, and rich colors',
            'best_colors': ['Olive Green', 'Rust', 'Terracotta', 'Warm Brown', 'Gold', 'Mustard Yellow', 'Teal', 'Warm Burgundy'],
            'avoid_colors': ['Black', 'Fuchsia', 'Icy Blue', 'Bright White', 'Cool Pink'],
            'characteristics': 'Medium contrast with warm, earthy undertones. Often has golden or reddish tones in hair.'
        }
    }
    
    def __init__(self, db_manager=None):
        """Initialize the color palette analyzer with a database manager."""
        self.db = db_manager if db_manager else DatabaseManager()
    
    def get_user_color_season(self):
        """
        Get the user's personal color season.
        
        Returns:
            str: User's color season
        """
        try:
            query = "SELECT color_season FROM user_preferences LIMIT 1"
            result = self.db.execute_query(query, fetch_one=True)
            
            if result and result['color_season']:
                return result['color_season']
            else:
                # Default to Winter as specified by the user
                self.set_user_color_season('Winter')
                return 'Winter'
        except Exception as e:
            print(f"Error getting user color season: {e}")
            return 'Winter'  # Default to Winter as specified by the user
    
    def set_user_color_season(self, season):
        """
        Set the user's personal color season.
        
        Args:
            season (str): Color season ('Winter', 'Summer', 'Spring', or 'Autumn')
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if season not in self.COLOR_SEASONS:
                print(f"Error: Invalid color season. Must be one of: {', '.join(self.COLOR_SEASONS.keys())}")
                return False
            
            query = """
                UPDATE user_preferences
                SET color_season = ?
                WHERE pref_id = (SELECT pref_id FROM user_preferences LIMIT 1)
            """
            self.db.execute_query(query, (season,))
            
            # If no rows were updated, insert a new preference
            query = "SELECT COUNT(*) as count FROM user_preferences"
            result = self.db.execute_query(query, fetch_one=True)
            
            if result['count'] == 0:
                query = """
                    INSERT INTO user_preferences (color_season, notification_preferences)
                    VALUES (?, '{"outfit_calendar": true, "seasonal_transition": true}')
                """
                self.db.execute_query(query, (season,))
            
            return True
        except Exception as e:
            print(f"Error setting user color season: {e}")
            return False
    
    def get_color_season_info(self, season=None):
        """
        Get information about a color season.
        
        Args:
            season (str, optional): Color season. Defaults to user's season.
            
        Returns:
            dict: Color season information
        """
        if season is None:
            season = self.get_user_color_season()
        
        if season not in self.COLOR_SEASONS:
            print(f"Error: Invalid color season. Must be one of: {', '.join(self.COLOR_SEASONS.keys())}")
            return None
        
        return self.COLOR_SEASONS[season]
    
    def analyze_item_color_compatibility(self, item_id):
        """
        Analyze how well a clothing item's color matches the user's color season.
        
        Args:
            item_id (int): ID of the clothing item
            
        Returns:
            dict: Compatibility analysis
        """
        try:
            # Get the item
            item = self.db.get_clothing_item(item_id)
            if not item:
                print(f"Error: Item with ID {item_id} does not exist")
                return None
            
            # Get the user's color season
            season = self.get_user_color_season()
            season_info = self.get_color_season_info(season)
            
            # Analyze color compatibility
            item_color = item['color'].lower() if item['color'] else ''
            
            # Check if the color is in the best colors list
            best_match = any(best_color.lower() in item_color or item_color in best_color.lower() 
                            for best_color in season_info['best_colors'])
            
            # Check if the color is in the avoid colors list
            avoid_match = any(avoid_color.lower() in item_color or item_color in avoid_color.lower() 
                             for avoid_color in season_info['avoid_colors'])
            
            # Determine compatibility
            if best_match:
                compatibility = 'Excellent'
                message = f"This {item_color} item is an excellent match for your {season} color palette!"
            elif avoid_match:
                compatibility = 'Poor'
                message = f"This {item_color} item may not be the best match for your {season} color palette."
            else:
                compatibility = 'Neutral'
                message = f"This {item_color} item is a neutral match for your {season} color palette."
            
            return {
                'item_id': item_id,
                'item_name': item['name'],
                'item_color': item['color'],
                'user_season': season,
                'compatibility': compatibility,
                'message': message,
                'best_colors': season_info['best_colors'],
                'avoid_colors': season_info['avoid_colors']
            }
        except Exception as e:
            print(f"Error analyzing item color compatibility: {e}")
            return None
    
    def analyze_outfit_color_harmony(self, outfit_id):
        """
        Analyze the color harmony of an outfit.
        
        Args:
            outfit_id (int): ID of the outfit
            
        Returns:
            dict: Color harmony analysis
        """
        try:
            # Get the outfit
            outfit = self.db.get_outfit(outfit_id)
            if not outfit:
                print(f"Error: Outfit with ID {outfit_id} does not exist")
                return None
            
            # Get the user's color season
            season = self.get_user_color_season()
            season_info = self.get_color_season_info(season)
            
            # Get all items in the outfit
            items = outfit['items']
            
            # Count items by compatibility
            excellent_count = 0
            neutral_count = 0
            poor_count = 0
            
            # Analyze each item
            item_analyses = []
            for item in items:
                analysis = self.analyze_item_color_compatibility(item['item_id'])
                if analysis:
                    item_analyses.append(analysis)
                    
                    if analysis['compatibility'] == 'Excellent':
                        excellent_count += 1
                    elif analysis['compatibility'] == 'Neutral':
                        neutral_count += 1
                    elif analysis['compatibility'] == 'Poor':
                        poor_count += 1
            
            # Calculate overall harmony
            total_items = len(items)
            if total_items == 0:
                harmony_score = 0
                harmony_level = 'N/A'
                message = "This outfit doesn't have any items to analyze."
            else:
                harmony_score = (excellent_count * 100 + neutral_count * 50) / total_items
                
                if harmony_score >= 80:
                    harmony_level = 'Excellent'
                    message = f"This outfit has excellent color harmony for your {season} color palette!"
                elif harmony_score >= 60:
                    harmony_level = 'Good'
                    message = f"This outfit has good color harmony for your {season} color palette."
                elif harmony_score >= 40:
                    harmony_level = 'Fair'
                    message = f"This outfit has fair color harmony for your {season} color palette."
                else:
                    harmony_level = 'Poor'
                    message = f"This outfit may not have the best color harmony for your {season} color palette."
            
            return {
                'outfit_id': outfit_id,
                'outfit_name': outfit['name'],
                'user_season': season,
                'harmony_score': round(harmony_score, 1),
                'harmony_level': harmony_level,
                'message': message,
                'excellent_count': excellent_count,
                'neutral_count': neutral_count,
                'poor_count': poor_count,
                'total_items': total_items,
                'item_analyses': item_analyses
            }
        except Exception as e:
            print(f"Error analyzing outfit color harmony: {e}")
            return None
    
    def get_wardrobe_color_analysis(self):
        """
        Analyze the color distribution of the entire wardrobe.
        
        Returns:
            dict: Wardrobe color analysis
        """
        try:
            # Get all clothing items
            query = "SELECT * FROM clothing_items"
            items = self.db.execute_query(query, fetch_all=True)
            
            # Get the user's color season
            season = self.get_user_color_season()
            season_info = self.get_color_season_info(season)
            
            # Count items by color compatibility
            excellent_count = 0
            neutral_count = 0
            poor_count = 0
            
            # Count colors
            color_counts = {}
            
            for item in items:
                # Analyze color compatibility
                item_color = item['color'].lower() if item['color'] else ''
                
                # Update color counts
                if item_color:
                    if item_color in color_counts:
                        color_counts[item_color] += 1
                    else:
                        color_counts[item_color] = 1
                
                # Check compatibility
                best_match = any(best_color.lower() in item_color or item_color in best_color.lower() 
                                for best_color in season_info['best_colors'])
                
                avoid_match = any(avoid_color.lower() in item_color or item_color in avoid_color.lower() 
                                 for avoid_color in season_info['avoid_colors'])
                
                if best_match:
                    excellent_count += 1
                elif avoid_match:
                    poor_count += 1
                else:
                    neutral_count += 1
            
            # Calculate percentages
            total_items = len(items)
            if total_items == 0:
                excellent_percent = 0
                neutral_percent = 0
                poor_percent = 0
            else:
                excellent_percent = round(excellent_count / total_items * 100, 1)
                neutral_percent = round(neutral_count / total_items * 100, 1)
                poor_percent = round(poor_count / total_items * 100, 1)
            
            # Sort colors by count
            sorted_colors = sorted(color_counts.items(), key=lambda x: x[1], reverse=True)
            
            # Generate recommendations
            recommendations = []
            
            if excellent_percent < 50:
                recommendations.append(f"Consider adding more {season}-friendly colors to your wardrobe.")
                recommendations.append(f"Look for items in these colors: {', '.join(season_info['best_colors'][:5])}")
            
            if poor_percent > 20:
                recommendations.append(f"You have many items that may not be ideal for your {season} color palette.")
                recommendations.append(f"When shopping, try to avoid: {', '.join(season_info['avoid_colors'][:5])}")
            
            # Find missing best colors
            missing_colors = []
            for best_color in season_info['best_colors']:
                best_color_lower = best_color.lower()
                if not any(best_color_lower in color.lower() or color.lower() in best_color_lower for color in color_counts.keys()):
                    missing_colors.append(best_color)
            
            if missing_colors:
                recommendations.append(f"Consider adding these missing colors to your wardrobe: {', '.join(missing_colors[:5])}")
            
            return {
                'user_season': season,
                'total_items': total_items,
                'excellent_count': excellent_count,
                'excellent_percent': excellent_percent,
                'neutral_count': neutral_count,
                'neutral_percent': neutral_percent,
                'poor_count': poor_count,
                'poor_percent': poor_percent,
                'top_colors': sorted_colors[:10],
                'recommendations': recommendations,
                'season_info': season_info
            }
        except Exception as e:
            print(f"Error getting wardrobe color analysis: {e}")
            return None


# Example usage
if __name__ == "__main__":
    analyzer = ColorPaletteAnalyzer()
    
    # Set user color season
    analyzer.set_user_color_season('Winter')
    
    # Get color season info
    season_info = analyzer.get_color_season_info()
    print(f"Winter color season info: {season_info['description']}")
    
    # Analyze wardrobe colors
    wardrobe_analysis = analyzer.get_wardrobe_color_analysis()
    if wardrobe_analysis:
        print(f"Wardrobe color analysis: {wardrobe_analysis['excellent_percent']}% excellent compatibility")
        
        for recommendation in wardrobe_analysis['recommendations']:
            print(f"- {recommendation}")
    
    # Analyze an outfit
    outfit_analysis = analyzer.analyze_outfit_color_harmony(1)
    if outfit_analysis:
        print(f"Outfit harmony: {outfit_analysis['harmony_level']} ({outfit_analysis['harmony_score']}%)")
        print(outfit_analysis['message'])
