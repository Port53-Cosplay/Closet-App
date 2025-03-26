#!/usr/bin/env python3
"""
Database operations module for the Clothing Database System.
This module provides CRUD operations for clothing items, outfits, and tags.
Thread-safe version that creates new connections for each operation.
"""

import os
import sqlite3
from datetime import datetime
import shutil
import threading

# Define the database directory and file
DB_DIR = os.path.dirname(os.path.abspath(__file__))
DB_FILE = os.path.expanduser("~/clothing_database.db")
PHOTOS_DIR = os.path.join(DB_DIR, "photos")

class DatabaseManager:
    """Thread-safe class to manage database operations for the Clothing Database System."""
    
    def __init__(self):
        """Initialize the database manager."""
        # No persistent connection in __init__ to ensure thread safety
        pass
    
    def _get_connection(self):
        """
        Get a new database connection.
        
        Returns:
            sqlite3.Connection: A new database connection
        """
        conn = sqlite3.connect(DB_FILE)
        # Enable foreign key constraints
        conn.execute("PRAGMA foreign_keys = ON")
        # Configure SQLite to return rows as dictionaries
        conn.row_factory = sqlite3.Row
        return conn
    
    def execute_query(self, query, params=(), fetch_one=False, fetch_all=False):
        """
        Execute a database query with thread safety.
        
        Args:
            query (str): SQL query to execute
            params (tuple or list): Parameters for the query
            fetch_one (bool): Whether to fetch one result
            fetch_all (bool): Whether to fetch all results
            
        Returns:
            Various: Query results based on fetch parameters
        """
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(query, params)
            
            if fetch_one:
                result = cursor.fetchone()
                return dict(result) if result else None
            elif fetch_all:
                return [dict(row) for row in cursor.fetchall()]
            else:
                conn.commit()
                return cursor.lastrowid if cursor.lastrowid else cursor.rowcount
        finally:
            conn.close()
    
    # ---- Clothing Item Operations ----
    
    def add_clothing_item(self, name, item_type, color, brand=None, size=None, 
                          material=None, season=None, occasion=None, 
                          purchase_date=None, photo_path=None, notes=None):
        """
        Add a new clothing item to the database.
        
        Args:
            name (str): Name/description of the item
            item_type (str): Type/category of the item
            color (str): Color of the item
            brand (str, optional): Brand of the item
            size (str, optional): Size of the item
            material (str, optional): Material of the item
            season (str, optional): Season for the item
            occasion (str, optional): Occasion for the item
            purchase_date (str, optional): Purchase date in YYYY-MM-DD format
            photo_path (str, optional): Path to the item's photo
            notes (str, optional): Additional notes about the item
            
        Returns:
            int: ID of the newly added item
        """
        query = '''
        INSERT INTO CLOTHING_ITEMS (
            name, type, color, brand, size, material, 
            season, occasion, purchase_date, photo_path, notes
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        '''
        params = (name, item_type, color, brand, size, material, 
                  season, occasion, purchase_date, photo_path, notes)
        
        return self.execute_query(query, params)
    
    def get_clothing_item(self, item_id):
        """
        Get a clothing item by ID.
        
        Args:
            item_id (int): ID of the clothing item
            
        Returns:
            dict: Clothing item data or None if not found
        """
        query = 'SELECT * FROM CLOTHING_ITEMS WHERE item_id = ?'
        return self.execute_query(query, (item_id,), fetch_one=True)
    
    def get_all_clothing_items(self, filters=None):
        """
        Get all clothing items, optionally filtered.
        
        Args:
            filters (dict, optional): Filters to apply (e.g., {'type': 'shirt'})
            
        Returns:
            list: List of clothing items as dictionaries
        """
        query = 'SELECT * FROM CLOTHING_ITEMS'
        params = []
        
        if filters:
            conditions = []
            for key, value in filters.items():
                if value:
                    conditions.append(f"{key} = ?")
                    params.append(value)
            
            if conditions:
                query += ' WHERE ' + ' AND '.join(conditions)
        
        return self.execute_query(query, params, fetch_all=True)
    
    def update_clothing_item(self, item_id, **kwargs):
        """
        Update a clothing item.
        
        Args:
            item_id (int): ID of the clothing item to update
            **kwargs: Fields to update (e.g., name='New Name', color='Blue')
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not kwargs:
            return False
        
        # Build the SET part of the query
        set_clause = ', '.join([f"{key} = ?" for key in kwargs.keys()])
        params = list(kwargs.values())
        params.append(item_id)
        
        query = f'''
        UPDATE CLOTHING_ITEMS
        SET {set_clause}
        WHERE item_id = ?
        '''
        
        result = self.execute_query(query, params)
        return result > 0
    
    def delete_clothing_item(self, item_id):
        """
        Delete a clothing item.
        
        Args:
            item_id (int): ID of the clothing item to delete
            
        Returns:
            bool: True if successful, False otherwise
        """
        # First, get the photo path to delete the photo file if it exists
        query = 'SELECT photo_path FROM CLOTHING_ITEMS WHERE item_id = ?'
        row = self.execute_query(query, (item_id,), fetch_one=True)
        
        if row and row['photo_path']:
            photo_path = row['photo_path']
            if os.path.exists(photo_path):
                try:
                    os.remove(photo_path)
                except OSError:
                    pass  # Ignore errors if file can't be deleted
        
        # Delete the item from the database
        query = 'DELETE FROM CLOTHING_ITEMS WHERE item_id = ?'
        result = self.execute_query(query, (item_id,))
        
        return result > 0
    
    def add_photo_to_item(self, item_id, photo_file_path):
        """
        Add or update a photo for a clothing item.
        
        Args:
            item_id (int): ID of the clothing item
            photo_file_path (str): Path to the photo file
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not os.path.exists(photo_file_path):
            return False
        
        # Create destination directory if it doesn't exist
        dest_dir = os.path.join(PHOTOS_DIR, "items")
        os.makedirs(dest_dir, exist_ok=True)
        
        # Generate a unique filename
        file_ext = os.path.splitext(photo_file_path)[1]
        new_filename = f"item_{item_id}{file_ext}"
        dest_path = os.path.join(dest_dir, new_filename)
        
        # Copy the file
        try:
            shutil.copy2(photo_file_path, dest_path)
        except (shutil.Error, OSError):
            return False
        
        # Update the database
        query = '''
        UPDATE CLOTHING_ITEMS
        SET photo_path = ?
        WHERE item_id = ?
        '''
        
        result = self.execute_query(query, (dest_path, item_id))
        return result > 0
    
    # ---- Outfit Operations ----
    
    def add_outfit(self, name, description=None, photo_path=None, rating=None):
        """
        Add a new outfit to the database.
        
        Args:
            name (str): Name of the outfit
            description (str, optional): Description of the outfit
            photo_path (str, optional): Path to the outfit's photo
            rating (int, optional): Rating of the outfit (1-5)
            
        Returns:
            int: ID of the newly added outfit
        """
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        query = '''
        INSERT INTO OUTFITS (
            name, description, created_date, modified_date, photo_path, rating
        ) VALUES (?, ?, ?, ?, ?, ?)
        '''
        
        return self.execute_query(query, (name, description, now, now, photo_path, rating))
    
    def get_outfit(self, outfit_id):
        """
        Get an outfit by ID.
        
        Args:
            outfit_id (int): ID of the outfit
            
        Returns:
            dict: Outfit data or None if not found
        """
        query = 'SELECT * FROM OUTFITS WHERE outfit_id = ?'
        outfit = self.execute_query(query, (outfit_id,), fetch_one=True)
        
        if not outfit:
            return None
        
        # Get the items in this outfit
        query = '''
        SELECT ci.*
        FROM CLOTHING_ITEMS ci
        JOIN OUTFIT_ITEMS oi ON ci.item_id = oi.item_id
        WHERE oi.outfit_id = ?
        '''
        
        items = self.execute_query(query, (outfit_id,), fetch_all=True)
        outfit['items'] = items
        
        # Get the tags for this outfit
        query = '''
        SELECT t.*, tc.name as category_name
        FROM TAGS t
        JOIN OUTFIT_TAGS ot ON t.tag_id = ot.tag_id
        LEFT JOIN TAG_CATEGORIES tc ON t.category_id = tc.category_id
        WHERE ot.outfit_id = ?
        '''
        
        tags = self.execute_query(query, (outfit_id,), fetch_all=True)
        outfit['tags'] = tags
        
        return outfit
    
    def get_all_outfits(self, filters=None):
        """
        Get all outfits, optionally filtered.
        
        Args:
            filters (dict, optional): Filters to apply
            
        Returns:
            list: List of outfits as dictionaries
        """
        query = 'SELECT * FROM OUTFITS'
        params = []
        
        if filters:
            conditions = []
            for key, value in filters.items():
                if value:
                    conditions.append(f"{key} = ?")
                    params.append(value)
            
            if conditions:
                query += ' WHERE ' + ' AND '.join(conditions)
        
        outfits = self.execute_query(query, params, fetch_all=True)
        
        # Get items and tags for each outfit
        for outfit in outfits:
            # Get items
            query = '''
            SELECT ci.*
            FROM CLOTHING_ITEMS ci
            JOIN OUTFIT_ITEMS oi ON ci.item_id = oi.item_id
            WHERE oi.outfit_id = ?
            '''
            
            items = self.execute_query(query, (outfit['outfit_id'],), fetch_all=True)
            outfit['items'] = items
            
            # Get tags
            query = '''
            SELECT t.*, tc.name as category_name
            FROM TAGS t
            JOIN OUTFIT_TAGS ot ON t.tag_id = ot.tag_id
            LEFT JOIN TAG_CATEGORIES tc ON t.category_id = tc.category_id
            WHERE ot.outfit_id = ?
            '''
            
            tags = self.execute_query(query, (outfit['outfit_id'],), fetch_all=True)
            outfit['tags'] = tags
        
        return outfits
    
    def update_outfit(self, outfit_id, **kwargs):
        """
        Update an outfit.
        
        Args:
            outfit_id (int): ID of the outfit to update
            **kwargs: Fields to update
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not kwargs:
            return False
        
        # Add modified date
        kwargs['modified_date'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Build the SET part of the query
        set_clause = ', '.join([f"{key} = ?" for key in kwargs.keys()])
        params = list(kwargs.values())
        params.append(outfit_id)
        
        query = f'''
        UPDATE OUTFITS
        SET {set_clause}
        WHERE outfit_id = ?
        '''
        
        result = self.execute_query(query, params)
        return result > 0
    
    def delete_outfit(self, outfit_id):
        """
        Delete an outfit.
        
        Args:
            outfit_id (int): ID of the outfit to delete
            
        Returns:
            bool: True if successful, False otherwise
        """
        # First, get the photo path to delete the photo file if it exists
        query = 'SELECT photo_path FROM OUTFITS WHERE outfit_id = ?'
        row = self.execute_query(query, (outfit_id,), fetch_one=True)
        
        if row and row['photo_path']:
            photo_path = row['photo_path']
            if os.path.exists(photo_path):
                try:
                    os.remove(photo_path)
                except OSError:
                    pass  # Ignore errors if file can't be deleted
        
        # Delete the outfit from the database
        query = 'DELETE FROM OUTFITS WHERE outfit_id = ?'
        result = self.execute_query(query, (outfit_id,))
        
        return result > 0
    
    def add_photo_to_outfit(self, outfit_id, photo_file_path):
        """
        Add or update a photo for an outfit.
        
        Args:
            outfit_id (int): ID of the outfit
            photo_file_path (str): Path to the photo file
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not os.path.exists(photo_file_path):
            return False
        
        # Create destination directory if it doesn't exist
        dest_dir = os.path.join(PHOTOS_DIR, "outfits")
        os.makedirs(dest_dir, exist_ok=True)
        
        # Generate a unique filename
        file_ext = os.path.splitext(photo_file_path)[1]
        new_filename = f"outfit_{outfit_id}{file_ext}"
        dest_path = os.path.join(dest_dir, new_filename)
        
        # Copy the file
        try:
            shutil.copy2(photo_file_path, dest_path)
        except (shutil.Error, OSError):
            return False
        
        # Update the database
        query = '''
        UPDATE OUTFITS
        SET photo_path = ?
        WHERE outfit_id = ?
        '''
        
        result = self.execute_query(query, (dest_path, outfit_id))
        return result > 0
    
    # ---- Outfit Items Operations ----
    
    def add_item_to_outfit(self, outfit_id, item_id):
        """
        Add a clothing item to an outfit.
        
        Args:
            outfit_id (int): ID of the outfit
            item_id (int): ID of the clothing item
            
        Returns:
            bool: True if successful, False otherwise
        """
        # Check if the item is already in the outfit
        query = '''
        SELECT COUNT(*) as count
        FROM OUTFIT_ITEMS
        WHERE outfit_id = ? AND item_id = ?
        '''
        
        result = self.execute_query(query, (outfit_id, item_id), fetch_one=True)
        
        if result and result['count'] > 0:
            return True  # Item is already in the outfit
        
        # Add the item to the outfit
        query = '''
        INSERT INTO OUTFIT_ITEMS (outfit_id, item_id)
        VALUES (?, ?)
        '''
        
        result = self.execute_query(query, (outfit_id, item_id))
        
        # Update the outfit's modified date
        self.update_outfit(outfit_id)
        
        return result > 0
    
    def remove_item_from_outfit(self, outfit_id, item_id):
        """
        Remove a clothing item from an outfit.
        
        Args:
            outfit_id (int): ID of the outfit
            item_id (int): ID of the clothing item
            
        Returns:
            bool: True if successful, False otherwise
        """
        query = '''
        DELETE FROM OUTFIT_ITEMS
        WHERE outfit_id = ? AND item_id = ?
        '''
        
        result = self.execute_query(query, (outfit_id, item_id))
        
        # Update the outfit's modified date
        self.update_outfit(outfit_id)
        
        return result > 0
    
    # ---- Tag Operations ----
    
    def add_tag_category(self, name, description=None):
        """
        Add a new tag category.
        
        Args:
            name (str): Name of the category
            description (str, optional): Description of the category
            
        Returns:
            int: ID of the newly added category
        """
        query = '''
        INSERT INTO TAG_CATEGORIES (name, description)
        VALUES (?, ?)
        '''
        
        return self.execute_query(query, (name, description))
    
    def get_tag_category(self, category_id):
        """
        Get a tag category by ID.
        
        Args:
            category_id (int): ID of the tag category
            
        Returns:
            dict: Tag category data or None if not found
        """
        query = 'SELECT * FROM TAG_CATEGORIES WHERE category_id = ?'
        return self.execute_query(query, (category_id,), fetch_one=True)
    
    def get_all_tag_categories(self):
        """
        Get all tag categories.
        
        Returns:
            list: List of tag categories as dictionaries
        """
        query = 'SELECT * FROM TAG_CATEGORIES'
        return self.execute_query(query, fetch_all=True)
    
    def add_tag(self, name, category_id=None, description=None):
        """
        Add a new tag.
        
        Args:
            name (str): Name of the tag
            category_id (int, optional): ID of the tag category
            description (str, optional): Description of the tag
            
        Returns:
            int: ID of the newly added tag
        """
        query = '''
        INSERT INTO TAGS (name, category_id, description)
        VALUES (?, ?, ?)
        '''
        
        return self.execute_query(query, (name, category_id, description))
    
    def get_tag(self, tag_id):
        """
        Get a tag by ID.
        
        Args:
            tag_id (int): ID of the tag
            
        Returns:
            dict: Tag data or None if not found
        """
        query = '''
        SELECT t.*, tc.name as category_name
        FROM TAGS t
        LEFT JOIN TAG_CATEGORIES tc ON t.category_id = tc.category_id
        WHERE t.tag_id = ?
        '''
        
        return self.execute_query(query, (tag_id,), fetch_one=True)
    
    def get_all_tags(self, category_id=None):
        """
        Get all tags, optionally filtered by category.
        
        Args:
            category_id (int, optional): ID of the tag category
            
        Returns:
            list: List of tags as dictionaries
        """
        if category_id:
            query = '''
            SELECT t.*, tc.name as category_name
            FROM TAGS t
            LEFT JOIN TAG_CATEGORIES tc ON t.category_id = tc.category_id
            WHERE t.category_id = ?
            '''
            return self.execute_query(query, (category_id,), fetch_all=True)
        else:
            query = '''
            SELECT t.*, tc.name as category_name
            FROM TAGS t
            LEFT JOIN TAG_CATEGORIES tc ON t.category_id = tc.category_id
            '''
            return self.execute_query(query, fetch_all=True)
    
    def add_tag_to_outfit(self, outfit_id, tag_id):
        """
        Add a tag to an outfit.
        
        Args:
            outfit_id (int): ID of the outfit
            tag_id (int): ID of the tag
            
        Returns:
            bool: True if successful, False otherwise
        """
        # Check if the tag is already on the outfit
        query = '''
        SELECT COUNT(*) as count
        FROM OUTFIT_TAGS
        WHERE outfit_id = ? AND tag_id = ?
        '''
        
        result = self.execute_query(query, (outfit_id, tag_id), fetch_one=True)
        
        if result and result['count'] > 0:
            return True  # Tag is already on the outfit
        
        # Add the tag to the outfit
        query = '''
        INSERT INTO OUTFIT_TAGS (outfit_id, tag_id)
        VALUES (?, ?)
        '''
        
        result = self.execute_query(query, (outfit_id, tag_id))
        
        # Update the outfit's modified date
        self.update_outfit(outfit_id)
        
        return result > 0
    
    def remove_tag_from_outfit(self, outfit_id, tag_id):
        """
        Remove a tag from an outfit.
        
        Args:
            outfit_id (int): ID of the outfit
            tag_id (int): ID of the tag
            
        Returns:
            bool: True if successful, False otherwise
        """
        query = '''
        DELETE FROM OUTFIT_TAGS
        WHERE outfit_id = ? AND tag_id = ?
        '''
        
        result = self.execute_query(query, (outfit_id, tag_id))
        
        # Update the outfit's modified date
        self.update_outfit(outfit_id)
        
        return result > 0
    
    # ---- Search Operations ----
    
    def find_outfits_by_item(self, item_id):
        """
        Find all outfits that contain a specific clothing item.
        
        Args:
            item_id (int): ID of the clothing item
            
        Returns:
            list: List of outfits as dictionaries
        """
        query = '''
        SELECT o.*
        FROM OUTFITS o
        JOIN OUTFIT_ITEMS oi ON o.outfit_id = oi.outfit_id
        WHERE oi.item_id = ?
        '''
        
        outfits = self.execute_query(query, (item_id,), fetch_all=True)
        
        # Get items and tags for each outfit
        for outfit in outfits:
            # Get items
            query = '''
            SELECT ci.*
            FROM CLOTHING_ITEMS ci
            JOIN OUTFIT_ITEMS oi ON ci.item_id = oi.item_id
            WHERE oi.outfit_id = ?
            '''
            
            items = self.execute_query(query, (outfit['outfit_id'],), fetch_all=True)
            outfit['items'] = items
            
            # Get tags
            query = '''
            SELECT t.*, tc.name as category_name
            FROM TAGS t
            JOIN OUTFIT_TAGS ot ON t.tag_id = ot.tag_id
            LEFT JOIN TAG_CATEGORIES tc ON t.category_id = tc.category_id
            WHERE ot.outfit_id = ?
            '''
            
            tags = self.execute_query(query, (outfit['outfit_id'],), fetch_all=True)
            outfit['tags'] = tags
        
        return outfits
    
    def find_outfits_by_tag(self, tag_id):
        """
        Find all outfits that have a specific tag.
        
        Args:
            tag_id (int): ID of the tag
            
        Returns:
            list: List of outfits as dictionaries
        """
        query = '''
        SELECT o.*
        FROM OUTFITS o
        JOIN OUTFIT_TAGS ot ON o.outfit_id = ot.outfit_id
        WHERE ot.tag_id = ?
        '''
        
        outfits = self.execute_query(query, (tag_id,), fetch_all=True)
        
        # Get items and tags for each outfit
        for outfit in outfits:
            # Get items
            query = '''
            SELECT ci.*
            FROM CLOTHING_ITEMS ci
            JOIN OUTFIT_ITEMS oi ON ci.item_id = oi.item_id
            WHERE oi.outfit_id = ?
            '''
            
            items = self.execute_query(query, (outfit['outfit_id'],), fetch_all=True)
            outfit['items'] = items
            
            # Get tags
            query = '''
            SELECT t.*, tc.name as category_name
            FROM TAGS t
            JOIN OUTFIT_TAGS ot ON t.tag_id = ot.tag_id
            LEFT JOIN TAG_CATEGORIES tc ON t.category_id = tc.category_id
            WHERE ot.outfit_id = ?
            '''
            
            tags = self.execute_query(query, (outfit['outfit_id'],), fetch_all=True)
            outfit['tags'] = tags
        
        return outfits
    
    def search_outfits(self, search_term):
        """
        Search for outfits by name or description.
        
        Args:
            search_term (str): Search term
            
        Returns:
            list: List of matching outfits as dictionaries
        """
        query = '''
        SELECT *
        FROM OUTFITS
        WHERE name LIKE ? OR description LIKE ?
        '''
        
        search_pattern = f"%{search_term}%"
        outfits = self.execute_query(query, (search_pattern, search_pattern), fetch_all=True)
        
        # Get items and tags for each outfit
        for outfit in outfits:
            # Get items
            query = '''
            SELECT ci.*
            FROM CLOTHING_ITEMS ci
            JOIN OUTFIT_ITEMS oi ON ci.item_id = oi.item_id
            WHERE oi.outfit_id = ?
            '''
            
            items = self.execute_query(query, (outfit['outfit_id'],), fetch_all=True)
            outfit['items'] = items
            
            # Get tags
            query = '''
            SELECT t.*, tc.name as category_name
            FROM TAGS t
            JOIN OUTFIT_TAGS ot ON t.tag_id = ot.tag_id
            LEFT JOIN TAG_CATEGORIES tc ON t.category_id = tc.category_id
            WHERE ot.outfit_id = ?
            '''
            
            tags = self.execute_query(query, (outfit['outfit_id'],), fetch_all=True)
            outfit['tags'] = tags
        
        return outfits
    
    def search_items(self, search_term):
        """
        Search for clothing items by name, type, color, etc.
        
        Args:
            search_term (str): Search term
            
        Returns:
            list: List of matching clothing items as dictionaries
        """
        query = '''
        SELECT *
        FROM CLOTHING_ITEMS
        WHERE name LIKE ? OR type LIKE ? OR color LIKE ? OR brand LIKE ? OR notes LIKE ?
        '''
        
        search_pattern = f"%{search_term}%"
        return self.execute_query(query, (search_pattern, search_pattern, search_pattern, search_pattern, search_pattern), fetch_all=True)
    
    # ---- Laundry Tracker Operations ----
    
    def mark_item_as_dirty(self, item_id):
        """
        Mark a clothing item as dirty (in laundry).
        
        Args:
            item_id (int): ID of the clothing item
            
        Returns:
            bool: True if successful, False otherwise
        """
        query = '''
        UPDATE CLOTHING_ITEMS
        SET laundry_status = 'dirty'
        WHERE item_id = ?
        '''
        
        result = self.execute_query(query, (item_id,))
        return result > 0
    
    def mark_item_as_clean(self, item_id):
        """
        Mark a clothing item as clean.
        
        Args:
            item_id (int): ID of the clothing item
            
        Returns:
            bool: True if successful, False otherwise
        """
        query = '''
        UPDATE CLOTHING_ITEMS
        SET laundry_status = 'clean'
        WHERE item_id = ?
        '''
        
        result = self.execute_query(query, (item_id,))
        return result > 0
    
    def get_dirty_items(self):
        """
        Get all clothing items marked as dirty.
        
        Returns:
            list: List of dirty clothing items as dictionaries
        """
        query = '''
        SELECT *
        FROM CLOTHING_ITEMS
        WHERE laundry_status = 'dirty'
        '''
        
        return self.execute_query(query, fetch_all=True)
    
    def get_clean_items(self):
        """
        Get all clothing items marked as clean.
        
        Returns:
            list: List of clean clothing items as dictionaries
        """
        query = '''
        SELECT *
        FROM CLOTHING_ITEMS
        WHERE laundry_status = 'clean' OR laundry_status IS NULL
        '''
        
        return self.execute_query(query, fetch_all=True)
    
    # ---- Outfit Calendar Operations ----
    
    def schedule_outfit(self, outfit_id, date, notes=None):
        """
        Schedule an outfit for a specific date.
        
        Args:
            outfit_id (int): ID of the outfit
            date (str): Date in YYYY-MM-DD format
            notes (str, optional): Additional notes
            
        Returns:
            int: ID of the calendar entry
        """
        query = '''
        INSERT INTO OUTFIT_CALENDAR (outfit_id, date, notes)
        VALUES (?, ?, ?)
        '''
        
        return self.execute_query(query, (outfit_id, date, notes))
    
    def get_scheduled_outfit(self, date):
        """
        Get the outfit scheduled for a specific date.
        
        Args:
            date (str): Date in YYYY-MM-DD format
            
        Returns:
            dict: Calendar entry with outfit data or None if not found
        """
        query = '''
        SELECT oc.*, o.*
        FROM OUTFIT_CALENDAR oc
        JOIN OUTFITS o ON oc.outfit_id = o.outfit_id
        WHERE oc.date = ?
        '''
        
        calendar_entry = self.execute_query(query, (date,), fetch_one=True)
        
        if not calendar_entry:
            return None
        
        # Get the items in this outfit
        query = '''
        SELECT ci.*
        FROM CLOTHING_ITEMS ci
        JOIN OUTFIT_ITEMS oi ON ci.item_id = oi.item_id
        WHERE oi.outfit_id = ?
        '''
        
        items = self.execute_query(query, (calendar_entry['outfit_id'],), fetch_all=True)
        calendar_entry['items'] = items
        
        return calendar_entry
    
    def get_upcoming_outfits(self, days=7):
        """
        Get outfits scheduled for the upcoming days.
        
        Args:
            days (int): Number of days to look ahead
            
        Returns:
            list: List of calendar entries with outfit data
        """
        query = '''
        SELECT oc.*, o.*
        FROM OUTFIT_CALENDAR oc
        JOIN OUTFITS o ON oc.outfit_id = o.outfit_id
        WHERE oc.date >= date('now') AND oc.date <= date('now', '+' || ? || ' days')
        ORDER BY oc.date
        '''
        
        calendar_entries = self.execute_query(query, (days,), fetch_all=True)
        
        # Get items for each outfit
        for entry in calendar_entries:
            query = '''
            SELECT ci.*
            FROM CLOTHING_ITEMS ci
            JOIN OUTFIT_ITEMS oi ON ci.item_id = oi.item_id
            WHERE oi.outfit_id = ?
            '''
            
            items = self.execute_query(query, (entry['outfit_id'],), fetch_all=True)
            entry['items'] = items
        
        return calendar_entries
    
    def record_outfit_as_worn(self, outfit_id, date=None):
        """
        Record that an outfit was worn on a specific date.
        
        Args:
            outfit_id (int): ID of the outfit
            date (str, optional): Date in YYYY-MM-DD format, defaults to today
            
        Returns:
            int: ID of the wear record
        """
        if not date:
            date = datetime.now().strftime('%Y-%m-%d')
        
        query = '''
        INSERT INTO OUTFIT_WEAR_HISTORY (outfit_id, date)
        VALUES (?, ?)
        '''
        
        wear_id = self.execute_query(query, (outfit_id, date))
        
        # Mark all items in the outfit as dirty
        query = '''
        SELECT item_id
        FROM OUTFIT_ITEMS
        WHERE outfit_id = ?
        '''
        
        items = self.execute_query(query, (outfit_id,), fetch_all=True)
        
        for item in items:
            self.mark_item_as_dirty(item['item_id'])
        
        return wear_id
    
    def get_outfit_wear_history(self, outfit_id):
        """
        Get the wear history for a specific outfit.
        
        Args:
            outfit_id (int): ID of the outfit
            
        Returns:
            list: List of wear records as dictionaries
        """
        query = '''
        SELECT *
        FROM OUTFIT_WEAR_HISTORY
        WHERE outfit_id = ?
        ORDER BY date DESC
        '''
        
        return self.execute_query(query, (outfit_id,), fetch_all=True)
    
    # ---- Outfit Statistics Operations ----
    
    def get_most_worn_outfits(self, limit=5):
        """
        Get the most frequently worn outfits.
        
        Args:
            limit (int): Maximum number of outfits to return
            
        Returns:
            list: List of outfits with wear counts
        """
        query = '''
        SELECT o.*, COUNT(owh.wear_id) as wear_count
        FROM OUTFITS o
        JOIN OUTFIT_WEAR_HISTORY owh ON o.outfit_id = owh.outfit_id
        GROUP BY o.outfit_id
        ORDER BY wear_count DESC
        LIMIT ?
        '''
        
        return self.execute_query(query, (limit,), fetch_all=True)
    
    def get_most_worn_items(self, limit=5):
        """
        Get the most frequently worn clothing items.
        
        Args:
            limit (int): Maximum number of items to return
            
        Returns:
            list: List of items with wear counts
        """
        query = '''
        SELECT ci.*, COUNT(owh.wear_id) as wear_count
        FROM CLOTHING_ITEMS ci
        JOIN OUTFIT_ITEMS oi ON ci.item_id = oi.item_id
        JOIN OUTFIT_WEAR_HISTORY owh ON oi.outfit_id = owh.outfit_id
        GROUP BY ci.item_id
        ORDER BY wear_count DESC
        LIMIT ?
        '''
        
        return self.execute_query(query, (limit,), fetch_all=True)
    
    def get_orphaned_items(self, limit=10):
        """
        Get clothing items that are rarely or never used in outfits.
        
        Args:
            limit (int): Maximum number of items to return
            
        Returns:
            list: List of rarely used items
        """
        query = '''
        SELECT ci.*, COUNT(oi.outfit_id) as outfit_count
        FROM CLOTHING_ITEMS ci
        LEFT JOIN OUTFIT_ITEMS oi ON ci.item_id = oi.item_id
        GROUP BY ci.item_id
        ORDER BY outfit_count ASC
        LIMIT ?
        '''
        
        return self.execute_query(query, (limit,), fetch_all=True)
    
    # ---- Seasonal Transition Operations ----
    
    def get_seasonal_items(self, season):
        """
        Get clothing items for a specific season.
        
        Args:
            season (str): Season name (e.g., 'Summer', 'Winter')
            
        Returns:
            list: List of clothing items for the specified season
        """
        query = '''
        SELECT *
        FROM CLOTHING_ITEMS
        WHERE season = ? OR season = 'All-Season'
        '''
        
        return self.execute_query(query, (season,), fetch_all=True)
    
    def get_items_to_store(self, current_season, upcoming_season):
        """
        Get items to store when transitioning between seasons.
        
        Args:
            current_season (str): Current season name
            upcoming_season (str): Upcoming season name
            
        Returns:
            list: List of items to store
        """
        query = '''
        SELECT *
        FROM CLOTHING_ITEMS
        WHERE season = ? AND season != ? AND season != 'All-Season'
        '''
        
        return self.execute_query(query, (current_season, upcoming_season), fetch_all=True)
    
    def get_items_to_bring_out(self, current_season, upcoming_season):
        """
        Get items to bring out when transitioning between seasons.
        
        Args:
            current_season (str): Current season name
            upcoming_season (str): Upcoming season name
            
        Returns:
            list: List of items to bring out
        """
        query = '''
        SELECT *
        FROM CLOTHING_ITEMS
        WHERE season = ? AND season != ? AND season != 'All-Season'
        '''
        
        return self.execute_query(query, (upcoming_season, current_season), fetch_all=True)
    
    # ---- Color Palette Analysis Operations ----
    
    def get_items_by_color(self, color):
        """
        Get clothing items by color.
        
        Args:
            color (str): Color name
            
        Returns:
            list: List of clothing items with the specified color
        """
        query = '''
        SELECT *
        FROM CLOTHING_ITEMS
        WHERE color LIKE ?
        '''
        
        return self.execute_query(query, (f"%{color}%",), fetch_all=True)
    
    def get_color_distribution(self):
        """
        Get the distribution of colors in the wardrobe.
        
        Returns:
            list: List of colors with counts
        """
        query = '''
        SELECT color, COUNT(*) as count
        FROM CLOTHING_ITEMS
        GROUP BY color
        ORDER BY count DESC
        '''
        
        return self.execute_query(query, fetch_all=True)
