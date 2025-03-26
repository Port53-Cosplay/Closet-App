#!/usr/bin/env python3
"""
Outfit Calendar module for the Clothing Database System.
This module provides functionality to plan outfits for specific dates.
"""

import datetime
from db.db_operations import DatabaseManager

class OutfitCalendar:
    """Class to manage the outfit calendar."""
    
    def __init__(self, db_manager=None):
        """Initialize the outfit calendar with a database manager."""
        self.db = db_manager if db_manager else DatabaseManager()
    
    def schedule_outfit(self, outfit_id, date, notes=None):
        """
        Schedule an outfit for a specific date.
        
        Args:
            outfit_id (int): ID of the outfit
            date (str): Date in YYYY-MM-DD format
            notes (str, optional): Additional notes for this scheduled outfit
            
        Returns:
            int: ID of the calendar entry if successful, None otherwise
        """
        try:
            # Validate the date format
            datetime.datetime.strptime(date, '%Y-%m-%d')
            
            # Check if the outfit exists
            outfit = self.db.get_outfit(outfit_id)
            if not outfit:
                print(f"Error: Outfit with ID {outfit_id} does not exist")
                return None
            
            # Insert the calendar entry
            query = """
                INSERT INTO calendar_outfits (outfit_id, date, notes)
                VALUES (?, ?, ?)
            """
            self.db.execute_query(query, (outfit_id, date, notes))
            
            # Get the ID of the inserted entry
            query = "SELECT last_insert_rowid() as calendar_id"
            result = self.db.execute_query(query, fetch_one=True)
            return result['calendar_id'] if result else None
        except ValueError:
            print(f"Error: Invalid date format. Please use YYYY-MM-DD")
            return None
        except Exception as e:
            print(f"Error scheduling outfit: {e}")
            return None
    
    def get_outfit_for_date(self, date):
        """
        Get the scheduled outfit for a specific date.
        
        Args:
            date (str): Date in YYYY-MM-DD format
            
        Returns:
            dict: Outfit data for the specified date, or None if not found
        """
        try:
            # Validate the date format
            datetime.datetime.strptime(date, '%Y-%m-%d')
            
            # Get the calendar entry
            query = """
                SELECT c.calendar_id, c.outfit_id, c.date, c.notes, o.name as outfit_name
                FROM calendar_outfits c
                JOIN outfits o ON c.outfit_id = o.outfit_id
                WHERE c.date = ?
            """
            calendar_entry = self.db.execute_query(query, (date,), fetch_one=True)
            
            if not calendar_entry:
                return None
            
            # Get the outfit details
            outfit = self.db.get_outfit(calendar_entry['outfit_id'])
            
            # Combine the data
            return {
                'calendar_id': calendar_entry['calendar_id'],
                'date': calendar_entry['date'],
                'notes': calendar_entry['notes'],
                'outfit': outfit
            }
        except ValueError:
            print(f"Error: Invalid date format. Please use YYYY-MM-DD")
            return None
        except Exception as e:
            print(f"Error getting outfit for date: {e}")
            return None
    
    def get_outfits_for_week(self, start_date):
        """
        Get all scheduled outfits for a week starting from a specific date.
        
        Args:
            start_date (str): Starting date in YYYY-MM-DD format
            
        Returns:
            list: List of scheduled outfits for the week
        """
        try:
            # Validate the date format
            start = datetime.datetime.strptime(start_date, '%Y-%m-%d')
            
            # Calculate the end date (7 days later)
            end = start + datetime.timedelta(days=7)
            end_date = end.strftime('%Y-%m-%d')
            
            # Get the calendar entries
            query = """
                SELECT c.calendar_id, c.outfit_id, c.date, c.notes, o.name as outfit_name
                FROM calendar_outfits c
                JOIN outfits o ON c.outfit_id = o.outfit_id
                WHERE c.date >= ? AND c.date < ?
                ORDER BY c.date
            """
            calendar_entries = self.db.execute_query(query, (start_date, end_date), fetch_all=True)
            
            # Get the outfit details for each entry
            result = []
            for entry in calendar_entries:
                outfit = self.db.get_outfit(entry['outfit_id'])
                result.append({
                    'calendar_id': entry['calendar_id'],
                    'date': entry['date'],
                    'notes': entry['notes'],
                    'outfit': outfit
                })
            
            return result
        except ValueError:
            print(f"Error: Invalid date format. Please use YYYY-MM-DD")
            return []
        except Exception as e:
            print(f"Error getting outfits for week: {e}")
            return []
    
    def update_scheduled_outfit(self, calendar_id, outfit_id=None, date=None, notes=None):
        """
        Update a scheduled outfit.
        
        Args:
            calendar_id (int): ID of the calendar entry
            outfit_id (int, optional): New outfit ID
            date (str, optional): New date in YYYY-MM-DD format
            notes (str, optional): New notes
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Check if the calendar entry exists
            query = "SELECT * FROM calendar_outfits WHERE calendar_id = ?"
            entry = self.db.execute_query(query, (calendar_id,), fetch_one=True)
            
            if not entry:
                print(f"Error: Calendar entry with ID {calendar_id} does not exist")
                return False
            
            # Validate the date format if provided
            if date:
                datetime.datetime.strptime(date, '%Y-%m-%d')
            
            # Check if the outfit exists if provided
            if outfit_id:
                outfit = self.db.get_outfit(outfit_id)
                if not outfit:
                    print(f"Error: Outfit with ID {outfit_id} does not exist")
                    return False
            
            # Build the update query
            update_parts = []
            params = []
            
            if outfit_id is not None:
                update_parts.append("outfit_id = ?")
                params.append(outfit_id)
            
            if date is not None:
                update_parts.append("date = ?")
                params.append(date)
            
            if notes is not None:
                update_parts.append("notes = ?")
                params.append(notes)
            
            if not update_parts:
                # Nothing to update
                return True
            
            # Execute the update
            query = f"UPDATE calendar_outfits SET {', '.join(update_parts)} WHERE calendar_id = ?"
            params.append(calendar_id)
            self.db.execute_query(query, tuple(params))
            
            return True
        except ValueError:
            print(f"Error: Invalid date format. Please use YYYY-MM-DD")
            return False
        except Exception as e:
            print(f"Error updating scheduled outfit: {e}")
            return False
    
    def delete_scheduled_outfit(self, calendar_id):
        """
        Delete a scheduled outfit.
        
        Args:
            calendar_id (int): ID of the calendar entry
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Check if the calendar entry exists
            query = "SELECT * FROM calendar_outfits WHERE calendar_id = ?"
            entry = self.db.execute_query(query, (calendar_id,), fetch_one=True)
            
            if not entry:
                print(f"Error: Calendar entry with ID {calendar_id} does not exist")
                return False
            
            # Delete the entry
            query = "DELETE FROM calendar_outfits WHERE calendar_id = ?"
            self.db.execute_query(query, (calendar_id,))
            
            return True
        except Exception as e:
            print(f"Error deleting scheduled outfit: {e}")
            return False
    
    def get_today_outfit(self):
        """
        Get the scheduled outfit for today.
        
        Returns:
            dict: Outfit data for today, or None if not found
        """
        today = datetime.datetime.now().strftime('%Y-%m-%d')
        return self.get_outfit_for_date(today)
    
    def get_upcoming_outfits(self, days=7):
        """
        Get all scheduled outfits for the upcoming days.
        
        Args:
            days (int): Number of days to look ahead
            
        Returns:
            list: List of scheduled outfits for the upcoming days
        """
        today = datetime.datetime.now().strftime('%Y-%m-%d')
        return self.get_outfits_for_week(today)[:days]


# Example usage
if __name__ == "__main__":
    calendar = OutfitCalendar()
    
    # Schedule an outfit for tomorrow
    tomorrow = (datetime.datetime.now() + datetime.timedelta(days=1)).strftime('%Y-%m-%d')
    calendar_id = calendar.schedule_outfit(1, tomorrow, "Meeting with client")
    
    if calendar_id:
        print(f"Scheduled outfit with calendar ID: {calendar_id}")
        
        # Get the outfit for tomorrow
        outfit = calendar.get_outfit_for_date(tomorrow)
        if outfit:
            print(f"Outfit for tomorrow: {outfit['outfit']['name']}")
            
        # Update the scheduled outfit
        calendar.update_scheduled_outfit(calendar_id, notes="Important meeting with client")
        
        # Get upcoming outfits
        upcoming = calendar.get_upcoming_outfits()
        print(f"Upcoming outfits: {len(upcoming)}")
        
        # Delete the scheduled outfit
        calendar.delete_scheduled_outfit(calendar_id)
    else:
        print("Failed to schedule outfit")
