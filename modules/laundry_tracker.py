#!/usr/bin/env python3
"""
Laundry Tracker module for the Clothing Database System.
This module provides functionality to track the laundry status of clothing items.
"""

from db.db_operations import DatabaseManager

class LaundryTracker:
    """Class to manage the laundry status of clothing items."""
    
    def __init__(self, db_manager=None):
        """Initialize the laundry tracker with a database manager."""
        self.db = db_manager if db_manager else DatabaseManager()
    
    def mark_as_dirty(self, item_id):
        """
        Mark a clothing item as dirty (in laundry).
        
        Args:
            item_id (int): ID of the clothing item
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Update the item status in the database
            query = "UPDATE clothing_items SET status = 'dirty' WHERE item_id = ?"
            self.db.execute_query(query, (item_id,))
            return True
        except Exception as e:
            print(f"Error marking item as dirty: {e}")
            return False
    
    def mark_as_clean(self, item_id):
        """
        Mark a clothing item as clean (available for outfits).
        
        Args:
            item_id (int): ID of the clothing item
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Update the item status in the database
            query = "UPDATE clothing_items SET status = 'clean' WHERE item_id = ?"
            self.db.execute_query(query, (item_id,))
            return True
        except Exception as e:
            print(f"Error marking item as clean: {e}")
            return False
    
    def get_dirty_items(self):
        """
        Get all clothing items marked as dirty.
        
        Returns:
            list: List of dirty clothing items
        """
        try:
            query = "SELECT * FROM clothing_items WHERE status = 'dirty'"
            return self.db.execute_query(query, fetch_all=True)
        except Exception as e:
            print(f"Error getting dirty items: {e}")
            return []
    
    def get_clean_items(self):
        """
        Get all clothing items marked as clean.
        
        Returns:
            list: List of clean clothing items
        """
        try:
            query = "SELECT * FROM clothing_items WHERE status = 'clean'"
            return self.db.execute_query(query, fetch_all=True)
        except Exception as e:
            print(f"Error getting clean items: {e}")
            return []
    
    def mark_outfit_items_as_dirty(self, outfit_id):
        """
        Mark all items in an outfit as dirty after wearing.
        
        Args:
            outfit_id (int): ID of the outfit
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Get all items in the outfit
            query = """
                SELECT i.item_id 
                FROM clothing_items i
                JOIN outfit_items oi ON i.item_id = oi.item_id
                WHERE oi.outfit_id = ?
            """
            items = self.db.execute_query(query, (outfit_id,), fetch_all=True)
            
            # Mark each item as dirty
            for item in items:
                self.mark_as_dirty(item['item_id'])
            
            return True
        except Exception as e:
            print(f"Error marking outfit items as dirty: {e}")
            return False
    
    def get_item_status(self, item_id):
        """
        Get the laundry status of a specific clothing item.
        
        Args:
            item_id (int): ID of the clothing item
            
        Returns:
            str: Status of the item ('clean' or 'dirty')
        """
        try:
            query = "SELECT status FROM clothing_items WHERE item_id = ?"
            result = self.db.execute_query(query, (item_id,), fetch_one=True)
            return result['status'] if result else 'clean'
        except Exception as e:
            print(f"Error getting item status: {e}")
            return 'clean'
    
    def get_laundry_statistics(self):
        """
        Get statistics about clean vs. dirty items.
        
        Returns:
            dict: Statistics about laundry status
        """
        try:
            clean_count = len(self.get_clean_items())
            dirty_count = len(self.get_dirty_items())
            total_count = clean_count + dirty_count
            
            return {
                'clean_count': clean_count,
                'dirty_count': dirty_count,
                'total_count': total_count,
                'clean_percentage': round(clean_count / total_count * 100 if total_count > 0 else 0, 1),
                'dirty_percentage': round(dirty_count / total_count * 100 if total_count > 0 else 0, 1)
            }
        except Exception as e:
            print(f"Error getting laundry statistics: {e}")
            return {
                'clean_count': 0,
                'dirty_count': 0,
                'total_count': 0,
                'clean_percentage': 0,
                'dirty_percentage': 0
            }


# Example usage
if __name__ == "__main__":
    tracker = LaundryTracker()
    
    # Mark some items as dirty
    tracker.mark_as_dirty(1)
    tracker.mark_as_dirty(2)
    
    # Get dirty items
    dirty_items = tracker.get_dirty_items()
    print(f"Dirty items: {len(dirty_items)}")
    
    # Get clean items
    clean_items = tracker.get_clean_items()
    print(f"Clean items: {len(clean_items)}")
    
    # Get laundry statistics
    stats = tracker.get_laundry_statistics()
    print(f"Laundry statistics: {stats}")
    
    # Mark items as clean
    tracker.mark_as_clean(1)
    
    # Get updated statistics
    stats = tracker.get_laundry_statistics()
    print(f"Updated laundry statistics: {stats}")
