import sqlite3

# Connect to your database
conn = sqlite3.connect('clothing_database.db')  # Adjust path if needed
cursor = conn.cursor()

# Check if there's a ITEM_TYPES table
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='ITEM_TYPES'")
table_exists = cursor.fetchone()

if table_exists:
    # If ITEM_TYPES table exists, add Jewelry if it doesn't exist
    cursor.execute("SELECT * FROM ITEM_TYPES WHERE name='Jewelry'")
    if not cursor.fetchone():
        cursor.execute("INSERT INTO ITEM_TYPES (name) VALUES ('Jewelry')")
        print("Added 'Jewelry' to ITEM_TYPES table")
    else:
        print("'Jewelry' already exists in ITEM_TYPES table")
else:
    # If no ITEM_TYPES table, we need to check the form template
    print("No ITEM_TYPES table found. Checking how item types are stored...")
    
    # Let's check if there are any items in the database to see what types are used
    cursor.execute("SELECT DISTINCT type FROM CLOTHING_ITEMS")
    existing_types = cursor.fetchall()
    print(f"Existing item types in database: {[t[0] for t in existing_types if t[0]]}")
    
    # Add a new item with type 'Jewelry' as an example
    print("You can add a new item with type 'Jewelry' through the web interface")
    print("Or update your form.html template to include 'Jewelry' as an option")

conn.commit()
conn.close()
