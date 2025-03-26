#!/usr/bin/env python3
"""
Database setup script for the Clothing Database System.
This script creates the SQLite database and all required tables based on the schema design.
"""

import os
import sqlite3
from datetime import datetime

# Define the database directory and file
DB_DIR = os.path.dirname(os.path.abspath(__file__))
DB_FILE = os.path.join(DB_DIR, "clothing_database.db")
PHOTOS_DIR = os.path.join(DB_DIR, "photos")

def create_database():
    """Create the SQLite database and all required tables."""
    # Create photos directory if it doesn't exist
    if not os.path.exists(PHOTOS_DIR):
        os.makedirs(PHOTOS_DIR)
        os.makedirs(os.path.join(PHOTOS_DIR, "items"))
        os.makedirs(os.path.join(PHOTOS_DIR, "outfits"))
        print(f"Created photos directories at {PHOTOS_DIR}")
    
    # Connect to the database (creates it if it doesn't exist)
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # Enable foreign key constraints
    cursor.execute("PRAGMA foreign_keys = ON")
    
    # Create CLOTHING_ITEMS table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS CLOTHING_ITEMS (
        item_id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        type TEXT NOT NULL,
        color TEXT NOT NULL,
        brand TEXT,
        size TEXT,
        material TEXT,
        season TEXT,
        occasion TEXT,
        purchase_date DATE,
        photo_path TEXT,
        notes TEXT
    )
    ''')
    
    # Create OUTFITS table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS OUTFITS (
        outfit_id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        description TEXT,
        created_date DATETIME NOT NULL,
        modified_date DATETIME NOT NULL,
        photo_path TEXT,
        rating INTEGER
    )
    ''')
    
    # Create OUTFIT_ITEMS junction table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS OUTFIT_ITEMS (
        outfit_id INTEGER NOT NULL,
        item_id INTEGER NOT NULL,
        PRIMARY KEY (outfit_id, item_id),
        FOREIGN KEY (outfit_id) REFERENCES OUTFITS(outfit_id) ON DELETE CASCADE,
        FOREIGN KEY (item_id) REFERENCES CLOTHING_ITEMS(item_id) ON DELETE CASCADE
    )
    ''')
    
    # Create TAG_CATEGORIES table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS TAG_CATEGORIES (
        category_id INTEGER PRIMARY KEY,
        name TEXT NOT NULL UNIQUE,
        description TEXT
    )
    ''')
    
    # Create TAGS table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS TAGS (
        tag_id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        category_id INTEGER NOT NULL,
        FOREIGN KEY (category_id) REFERENCES TAG_CATEGORIES(category_id) ON DELETE CASCADE
    )
    ''')
    
    # Create OUTFIT_TAGS junction table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS OUTFIT_TAGS (
        outfit_id INTEGER NOT NULL,
        tag_id INTEGER NOT NULL,
        PRIMARY KEY (outfit_id, tag_id),
        FOREIGN KEY (outfit_id) REFERENCES OUTFITS(outfit_id) ON DELETE CASCADE,
        FOREIGN KEY (tag_id) REFERENCES TAGS(tag_id) ON DELETE CASCADE
    )
    ''')
    
    # Create indexes for optimizing search performance
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_clothing_type ON CLOTHING_ITEMS(type)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_clothing_color ON CLOTHING_ITEMS(color)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_clothing_season ON CLOTHING_ITEMS(season)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_clothing_occasion ON CLOTHING_ITEMS(occasion)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_tags_name ON TAGS(name)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_tags_category ON TAGS(category_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_outfit_items_item ON OUTFIT_ITEMS(item_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_outfit_tags_tag ON OUTFIT_TAGS(tag_id)')
    
    # Insert default tag categories
    default_categories = [
        (1, "Style", "Fashion style categories (e.g., casual, formal, bohemian)"),
        (2, "Theme", "Outfit themes (e.g., work, date night, weekend)"),
        (3, "Season", "Seasons (summer, winter, fall, spring)"),
        (4, "Color Scheme", "Color combinations (e.g., monochrome, pastel)"),
        (5, "Custom", "User-defined custom tags")
    ]
    
    cursor.executemany('''
    INSERT OR IGNORE INTO TAG_CATEGORIES (category_id, name, description)
    VALUES (?, ?, ?)
    ''', default_categories)
    
    # Insert default tags
    default_tags = [
        # Style tags
        (1, "Casual", 1),
        (2, "Formal", 1),
        (3, "Business", 1),
        (4, "Bohemian", 1),
        (5, "Minimalist", 1),
        (6, "Vintage", 1),
        (7, "Sporty", 1),
        
        # Theme tags
        (8, "Work", 2),
        (9, "Date Night", 2),
        (10, "Weekend", 2),
        (11, "Vacation", 2),
        (12, "Special Occasion", 2),
        
        # Season tags
        (13, "Summer", 3),
        (14, "Winter", 3),
        (15, "Fall", 3),
        (16, "Spring", 3),
        (17, "All-Season", 3),
        
        # Color scheme tags
        (18, "Monochrome", 4),
        (19, "Pastel", 4),
        (20, "Bright", 4),
        (21, "Earth Tones", 4),
        (22, "Neutral", 4)
    ]
    
    cursor.executemany('''
    INSERT OR IGNORE INTO TAGS (tag_id, name, category_id)
    VALUES (?, ?, ?)
    ''', default_tags)
    
    # Commit changes and close connection
    conn.commit()
    conn.close()
    
    print(f"Database created successfully at {DB_FILE}")
    print("All tables and default data have been created.")

if __name__ == "__main__":
    create_database()
