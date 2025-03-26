#!/usr/bin/env python3
"""
Database schema updates for additional features.
This script updates the database schema to support the additional features requested by the user.
"""

import sqlite3

def update_schema():
    """Update the database schema to support additional features."""
    conn = sqlite3.connect('clothing_database.db')
    cursor = conn.cursor()
    
    # Add status field to clothing_items table for laundry tracking
    cursor.execute('''
    ALTER TABLE clothing_items ADD COLUMN status TEXT DEFAULT 'clean'
    ''')
    
    # Create calendar_outfits table for outfit calendar
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS calendar_outfits (
        calendar_id INTEGER PRIMARY KEY AUTOINCREMENT,
        outfit_id INTEGER,
        date TEXT NOT NULL,
        notes TEXT,
        FOREIGN KEY (outfit_id) REFERENCES outfits (outfit_id) ON DELETE CASCADE
    )
    ''')
    
    # Create outfit_stats table for tracking outfit usage
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS outfit_stats (
        stat_id INTEGER PRIMARY KEY AUTOINCREMENT,
        outfit_id INTEGER,
        wear_date TEXT NOT NULL,
        rating INTEGER,
        notes TEXT,
        FOREIGN KEY (outfit_id) REFERENCES outfits (outfit_id) ON DELETE CASCADE
    )
    ''')
    
    # Create item_stats table for tracking item usage
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS item_stats (
        stat_id INTEGER PRIMARY KEY AUTOINCREMENT,
        item_id INTEGER,
        wear_date TEXT NOT NULL,
        outfit_id INTEGER,
        FOREIGN KEY (item_id) REFERENCES clothing_items (item_id) ON DELETE CASCADE,
        FOREIGN KEY (outfit_id) REFERENCES outfits (outfit_id) ON DELETE CASCADE
    )
    ''')
    
    # Create seasonal_transitions table for seasonal wardrobe transitions
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS seasonal_transitions (
        transition_id INTEGER PRIMARY KEY AUTOINCREMENT,
        season TEXT NOT NULL,
        start_date TEXT NOT NULL,
        end_date TEXT NOT NULL,
        notification_sent INTEGER DEFAULT 0
    )
    ''')
    
    # Add color_season field to user_preferences table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS user_preferences (
        pref_id INTEGER PRIMARY KEY AUTOINCREMENT,
        color_season TEXT,
        notification_preferences TEXT
    )
    ''')
    
    # Insert default user preferences if not exists
    cursor.execute('''
    INSERT INTO user_preferences (color_season, notification_preferences)
    SELECT 'winter', '{"outfit_calendar": true, "seasonal_transition": true}'
    WHERE NOT EXISTS (SELECT 1 FROM user_preferences)
    ''')
    
    conn.commit()
    conn.close()
    
    print("Database schema updated successfully for additional features.")

if __name__ == "__main__":
    update_schema()
