#!/usr/bin/env python3
"""
Outfit Statistics module for the Clothing Database System.
This module provides functionality to track and analyze outfit usage statistics.
"""

import datetime
from db.db_operations import DatabaseManager

class OutfitStatistics:
    """Class to manage outfit usage statistics."""
    
    def __init__(self, db_manager=None):
        """Initialize the outfit statistics with a database manager."""
        self.db = db_manager if db_manager else DatabaseManager()
    
    def record_outfit_wear(self, outfit_id, wear_date=None, rating=None, notes=None):
        """
        Record that an outfit was worn on a specific date.
        
        Args:
            outfit_id (int): ID of the outfit
            wear_date (str, optional): Date in YYYY-MM-DD format. Defaults to today.
            rating (int, optional): Rating from 1-5
            notes (str, optional): Additional notes about wearing this outfit
            
        Returns:
            int: ID of the stat entry if successful, None otherwise
        """
        try:
            # Default to today if no date provided
            if wear_date is None:
                wear_date = datetime.datetime.now().strftime('%Y-%m-%d')
            else:
                # Validate the date format
                datetime.datetime.strptime(wear_date, '%Y-%m-%d')
            
            # Check if the outfit exists
            outfit = self.db.get_outfit(outfit_id)
            if not outfit:
                print(f"Error: Outfit with ID {outfit_id} does not exist")
                return None
            
            # Insert the stat entry
            query = """
                INSERT INTO outfit_stats (outfit_id, wear_date, rating, notes)
                VALUES (?, ?, ?, ?)
            """
            self.db.execute_query(query, (outfit_id, wear_date, rating, notes))
            
            # Get the ID of the inserted entry
            query = "SELECT last_insert_rowid() as stat_id"
            result = self.db.execute_query(query, fetch_one=True)
            stat_id = result['stat_id'] if result else None
            
            # Record each item in the outfit as worn
            if stat_id:
                self._record_items_wear(outfit_id, wear_date)
            
            return stat_id
        except ValueError:
            print(f"Error: Invalid date format. Please use YYYY-MM-DD")
            return None
        except Exception as e:
            print(f"Error recording outfit wear: {e}")
            return None
    
    def _record_items_wear(self, outfit_id, wear_date):
        """
        Record that all items in an outfit were worn on a specific date.
        
        Args:
            outfit_id (int): ID of the outfit
            wear_date (str): Date in YYYY-MM-DD format
        """
        try:
            # Get all items in the outfit
            query = """
                SELECT item_id FROM outfit_items
                WHERE outfit_id = ?
            """
            items = self.db.execute_query(query, (outfit_id,), fetch_all=True)
            
            # Record each item as worn
            for item in items:
                query = """
                    INSERT INTO item_stats (item_id, wear_date, outfit_id)
                    VALUES (?, ?, ?)
                """
                self.db.execute_query(query, (item['item_id'], wear_date, outfit_id))
        except Exception as e:
            print(f"Error recording items wear: {e}")
    
    def get_outfit_wear_history(self, outfit_id):
        """
        Get the wear history for a specific outfit.
        
        Args:
            outfit_id (int): ID of the outfit
            
        Returns:
            list: List of wear history entries
        """
        try:
            query = """
                SELECT * FROM outfit_stats
                WHERE outfit_id = ?
                ORDER BY wear_date DESC
            """
            return self.db.execute_query(query, (outfit_id,), fetch_all=True)
        except Exception as e:
            print(f"Error getting outfit wear history: {e}")
            return []
    
    def get_item_wear_history(self, item_id):
        """
        Get the wear history for a specific item.
        
        Args:
            item_id (int): ID of the item
            
        Returns:
            list: List of wear history entries
        """
        try:
            query = """
                SELECT s.*, o.name as outfit_name
                FROM item_stats s
                LEFT JOIN outfits o ON s.outfit_id = o.outfit_id
                WHERE s.item_id = ?
                ORDER BY s.wear_date DESC
            """
            return self.db.execute_query(query, (item_id,), fetch_all=True)
        except Exception as e:
            print(f"Error getting item wear history: {e}")
            return []
    
    def get_most_worn_outfits(self, limit=10):
        """
        Get the most frequently worn outfits.
        
        Args:
            limit (int, optional): Maximum number of outfits to return
            
        Returns:
            list: List of outfits with wear count
        """
        try:
            query = """
                SELECT s.outfit_id, o.name, COUNT(*) as wear_count, 
                       AVG(s.rating) as avg_rating, MAX(s.wear_date) as last_worn
                FROM outfit_stats s
                JOIN outfits o ON s.outfit_id = o.outfit_id
                GROUP BY s.outfit_id
                ORDER BY wear_count DESC
                LIMIT ?
            """
            return self.db.execute_query(query, (limit,), fetch_all=True)
        except Exception as e:
            print(f"Error getting most worn outfits: {e}")
            return []
    
    def get_most_worn_items(self, limit=10):
        """
        Get the most frequently worn items.
        
        Args:
            limit (int, optional): Maximum number of items to return
            
        Returns:
            list: List of items with wear count
        """
        try:
            query = """
                SELECT s.item_id, i.name, i.type, i.color, COUNT(*) as wear_count, 
                       MAX(s.wear_date) as last_worn
                FROM item_stats s
                JOIN clothing_items i ON s.item_id = i.item_id
                GROUP BY s.item_id
                ORDER BY wear_count DESC
                LIMIT ?
            """
            return self.db.execute_query(query, (limit,), fetch_all=True)
        except Exception as e:
            print(f"Error getting most worn items: {e}")
            return []
    
    def get_least_worn_items(self, limit=10):
        """
        Get the least frequently worn items (orphaned items).
        
        Args:
            limit (int, optional): Maximum number of items to return
            
        Returns:
            list: List of items with wear count
        """
        try:
            query = """
                SELECT i.item_id, i.name, i.type, i.color, 
                       COUNT(s.stat_id) as wear_count,
                       MAX(s.wear_date) as last_worn
                FROM clothing_items i
                LEFT JOIN item_stats s ON i.item_id = s.item_id
                GROUP BY i.item_id
                ORDER BY wear_count ASC, i.name ASC
                LIMIT ?
            """
            return self.db.execute_query(query, (limit,), fetch_all=True)
        except Exception as e:
            print(f"Error getting least worn items: {e}")
            return []
    
    def get_highest_rated_outfits(self, limit=10):
        """
        Get the highest rated outfits.
        
        Args:
            limit (int, optional): Maximum number of outfits to return
            
        Returns:
            list: List of outfits with average rating
        """
        try:
            query = """
                SELECT s.outfit_id, o.name, AVG(s.rating) as avg_rating, 
                       COUNT(*) as wear_count, MAX(s.wear_date) as last_worn
                FROM outfit_stats s
                JOIN outfits o ON s.outfit_id = o.outfit_id
                WHERE s.rating IS NOT NULL
                GROUP BY s.outfit_id
                ORDER BY avg_rating DESC
                LIMIT ?
            """
            return self.db.execute_query(query, (limit,), fetch_all=True)
        except Exception as e:
            print(f"Error getting highest rated outfits: {e}")
            return []
    
    def get_outfit_statistics_summary(self):
        """
        Get a summary of outfit statistics.
        
        Returns:
            dict: Summary statistics
        """
        try:
            # Total number of outfits
            query = "SELECT COUNT(*) as total_outfits FROM outfits"
            total_outfits_result = self.db.execute_query(query, fetch_one=True)
            total_outfits = total_outfits_result['total_outfits'] if total_outfits_result else 0
            
            # Total number of items
            query = "SELECT COUNT(*) as total_items FROM clothing_items"
            total_items_result = self.db.execute_query(query, fetch_one=True)
            total_items = total_items_result['total_items'] if total_items_result else 0
            
            # Total number of wears
            query = "SELECT COUNT(*) as total_wears FROM outfit_stats"
            total_wears_result = self.db.execute_query(query, fetch_one=True)
            total_wears = total_wears_result['total_wears'] if total_wears_result else 0
            
            # Average rating
            query = "SELECT AVG(rating) as avg_rating FROM outfit_stats WHERE rating IS NOT NULL"
            avg_rating_result = self.db.execute_query(query, fetch_one=True)
            avg_rating = avg_rating_result['avg_rating'] if avg_rating_result and avg_rating_result['avg_rating'] else 0
            
            # Most recent wear
            query = "SELECT MAX(wear_date) as last_wear FROM outfit_stats"
            last_wear_result = self.db.execute_query(query, fetch_one=True)
            last_wear = last_wear_result['last_wear'] if last_wear_result else None
            
            # Number of unworn items
            query = """
                SELECT COUNT(*) as unworn_items
                FROM clothing_items i
                LEFT JOIN item_stats s ON i.item_id = s.item_id
                WHERE s.stat_id IS NULL
            """
            unworn_items_result = self.db.execute_query(query, fetch_one=True)
            unworn_items = unworn_items_result['unworn_items'] if unworn_items_result else 0
            
            return {
                'total_outfits': total_outfits,
                'total_items': total_items,
                'total_wears': total_wears,
                'avg_rating': round(avg_rating, 1) if avg_rating else 0,
                'last_wear': last_wear,
                'unworn_items': unworn_items,
                'unworn_percentage': round(unworn_items / total_items * 100, 1) if total_items > 0 else 0
            }
        except Exception as e:
            print(f"Error getting outfit statistics summary: {e}")
            return {
                'total_outfits': 0,
                'total_items': 0,
                'total_wears': 0,
                'avg_rating': 0,
                'last_wear': None,
                'unworn_items': 0,
                'unworn_percentage': 0
            }


# Example usage
if __name__ == "__main__":
    stats = OutfitStatistics()
    
    # Record an outfit wear
    stat_id = stats.record_outfit_wear(1, rating=5, notes="Received many compliments")
    
    if stat_id:
        print(f"Recorded outfit wear with stat ID: {stat_id}")
        
        # Get outfit wear history
        history = stats.get_outfit_wear_history(1)
        print(f"Outfit wear history: {len(history)} entries")
        
        # Get most worn outfits
        most_worn = stats.get_most_worn_outfits(5)
        print(f"Most worn outfits: {len(most_worn)}")
        
        # Get most worn items
        most_worn_items = stats.get_most_worn_items(5)
        print(f"Most worn items: {len(most_worn_items)}")
        
        # Get least worn items
        least_worn_items = stats.get_least_worn_items(5)
        print(f"Least worn items: {len(least_worn_items)}")
        
        # Get statistics summary
        summary = stats.get_outfit_statistics_summary()
        print(f"Statistics summary: {summary}")
    else:
        print("Failed to record outfit wear")
