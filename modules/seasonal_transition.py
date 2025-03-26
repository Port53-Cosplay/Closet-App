#!/usr/bin/env python3
"""
Seasonal Wardrobe Transition Helper for the Clothing Database System.
This module provides functionality to manage seasonal wardrobe transitions.
"""

import datetime
from db.db_operations import DatabaseManager

class SeasonalTransitionHelper:
    """Class to manage seasonal wardrobe transitions."""
    
    # Define seasons with their typical start and end dates
    SEASONS = {
        'Spring': {'start_month': 3, 'start_day': 20, 'end_month': 6, 'end_day': 20},
        'Summer': {'start_month': 6, 'start_day': 21, 'end_month': 9, 'end_day': 22},
        'Fall': {'start_month': 9, 'start_day': 23, 'end_month': 12, 'end_day': 20},
        'Winter': {'start_month': 12, 'start_day': 21, 'end_month': 3, 'end_day': 19}
    }
    
    def __init__(self, db_manager=None):
        """Initialize the seasonal transition helper with a database manager."""
        self.db = db_manager if db_manager else DatabaseManager()
    
    def setup_seasonal_transitions(self, year=None):
        """
        Set up seasonal transitions for a specific year.
        
        Args:
            year (int, optional): Year to set up transitions for. Defaults to current year.
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if year is None:
                year = datetime.datetime.now().year
            
            # Clear existing transitions for this year
            self._clear_transitions_for_year(year)
            
            # Set up transitions for each season
            for season, dates in self.SEASONS.items():
                start_month = dates['start_month']
                start_day = dates['start_day']
                end_month = dates['end_month']
                end_day = dates['end_day']
                
                # Handle winter spanning across years
                if season == 'Winter':
                    start_date = f"{year}-{start_month:02d}-{start_day:02d}"
                    end_date = f"{year+1}-{end_month:02d}-{end_day:02d}"
                else:
                    start_date = f"{year}-{start_month:02d}-{start_day:02d}"
                    end_date = f"{year}-{end_month:02d}-{end_day:02d}"
                
                # Insert the transition
                query = """
                    INSERT INTO seasonal_transitions (season, start_date, end_date, notification_sent)
                    VALUES (?, ?, ?, 0)
                """
                self.db.execute_query(query, (season, start_date, end_date))
            
            return True
        except Exception as e:
            print(f"Error setting up seasonal transitions: {e}")
            return False
    
    def _clear_transitions_for_year(self, year):
        """
        Clear existing transitions for a specific year.
        
        Args:
            year (int): Year to clear transitions for
        """
        try:
            # Delete transitions that start in the specified year
            query = "DELETE FROM seasonal_transitions WHERE start_date LIKE ?"
            self.db.execute_query(query, (f"{year}-%",))
        except Exception as e:
            print(f"Error clearing transitions for year {year}: {e}")
    
    def get_current_season(self):
        """
        Get the current season based on the date.
        
        Returns:
            str: Current season name
        """
        today = datetime.datetime.now().strftime('%Y-%m-%d')
        
        try:
            query = """
                SELECT season FROM seasonal_transitions
                WHERE ? BETWEEN start_date AND end_date
            """
            result = self.db.execute_query(query, (today,), fetch_one=True)
            
            return result['season'] if result else self._calculate_current_season()
        except Exception as e:
            print(f"Error getting current season: {e}")
            return self._calculate_current_season()
    
    def _calculate_current_season(self):
        """
        Calculate the current season based on the date.
        
        Returns:
            str: Current season name
        """
        now = datetime.datetime.now()
        month = now.month
        day = now.day
        
        if (month == 3 and day >= 20) or (month > 3 and month < 6) or (month == 6 and day <= 20):
            return 'Spring'
        elif (month == 6 and day >= 21) or (month > 6 and month < 9) or (month == 9 and day <= 22):
            return 'Summer'
        elif (month == 9 and day >= 23) or (month > 9 and month < 12) or (month == 12 and day <= 20):
            return 'Fall'
        else:
            return 'Winter'
    
    def get_upcoming_season(self):
        """
        Get the upcoming season based on the current date.
        
        Returns:
            dict: Upcoming season data with name and start date
        """
        current_season = self.get_current_season()
        
        # Define the next season
        next_seasons = {
            'Spring': 'Summer',
            'Summer': 'Fall',
            'Fall': 'Winter',
            'Winter': 'Spring'
        }
        
        upcoming_season = next_seasons[current_season]
        
        try:
            # Get the start date of the upcoming season
            today = datetime.datetime.now().strftime('%Y-%m-%d')
            
            query = """
                SELECT season, start_date FROM seasonal_transitions
                WHERE season = ? AND start_date > ?
                ORDER BY start_date ASC
                LIMIT 1
            """
            result = self.db.execute_query(query, (upcoming_season, today), fetch_one=True)
            
            if result:
                return {
                    'season': result['season'],
                    'start_date': result['start_date']
                }
            else:
                # If not found, it might be in the next year
                next_year = datetime.datetime.now().year + 1
                self.setup_seasonal_transitions(next_year)
                
                # Try again
                result = self.db.execute_query(query, (upcoming_season, today), fetch_one=True)
                
                if result:
                    return {
                        'season': result['season'],
                        'start_date': result['start_date']
                    }
                else:
                    # Fallback to calculated dates
                    return {
                        'season': upcoming_season,
                        'start_date': self._calculate_season_start_date(upcoming_season)
                    }
        except Exception as e:
            print(f"Error getting upcoming season: {e}")
            return {
                'season': upcoming_season,
                'start_date': self._calculate_season_start_date(upcoming_season)
            }
    
    def _calculate_season_start_date(self, season):
        """
        Calculate the start date of a season.
        
        Args:
            season (str): Season name
            
        Returns:
            str: Start date in YYYY-MM-DD format
        """
        now = datetime.datetime.now()
        year = now.year
        
        # If we're calculating for next year's season
        if season == 'Spring' and now.month > 3:
            year += 1
        elif season == 'Summer' and now.month > 6:
            year += 1
        elif season == 'Fall' and now.month > 9:
            year += 1
        elif season == 'Winter' and now.month > 12:
            year += 1
        
        month = self.SEASONS[season]['start_month']
        day = self.SEASONS[season]['start_day']
        
        return f"{year}-{month:02d}-{day:02d}"
    
    def get_seasonal_items(self, season):
        """
        Get all clothing items for a specific season.
        
        Args:
            season (str): Season name
            
        Returns:
            list: List of clothing items for the season
        """
        try:
            query = """
                SELECT * FROM clothing_items
                WHERE season LIKE ?
            """
            return self.db.execute_query(query, (f"%{season}%",), fetch_all=True)
        except Exception as e:
            print(f"Error getting seasonal items: {e}")
            return []
    
    def get_transition_recommendations(self):
        """
        Get recommendations for seasonal wardrobe transition.
        
        Returns:
            dict: Transition recommendations
        """
        current_season = self.get_current_season()
        upcoming_season = self.get_upcoming_season()
        
        # Get items for current and upcoming seasons
        current_items = self.get_seasonal_items(current_season)
        upcoming_items = self.get_seasonal_items(upcoming_season['season'])
        
        # Get all-season items
        all_season_items = self.get_seasonal_items('All-Season')
        
        # Items to store (current season items that are not in upcoming season)
        items_to_store = []
        for item in current_items:
            if item not in upcoming_items and item not in all_season_items:
                items_to_store.append(item)
        
        # Items to bring out (upcoming season items that are not in current season)
        items_to_bring_out = []
        for item in upcoming_items:
            if item not in current_items and item not in all_season_items:
                items_to_bring_out.append(item)
        
        return {
            'current_season': current_season,
            'upcoming_season': upcoming_season['season'],
            'transition_date': upcoming_season['start_date'],
            'days_until_transition': self._days_until_date(upcoming_season['start_date']),
            'items_to_store': items_to_store,
            'items_to_bring_out': items_to_bring_out,
            'all_season_items': all_season_items
        }
    
    def _days_until_date(self, date_str):
        """
        Calculate the number of days until a specific date.
        
        Args:
            date_str (str): Date in YYYY-MM-DD format
            
        Returns:
            int: Number of days until the date
        """
        try:
            target_date = datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
            today = datetime.datetime.now().date()
            delta = target_date - today
            return max(0, delta.days)
        except Exception as e:
            print(f"Error calculating days until date: {e}")
            return 0
    
    def check_transition_notification(self):
        """
        Check if a transition notification should be sent.
        
        Returns:
            dict: Notification data if a notification should be sent, None otherwise
        """
        try:
            today = datetime.datetime.now().date()
            
            # Get upcoming transitions
            query = """
                SELECT * FROM seasonal_transitions
                WHERE start_date > ? AND notification_sent = 0
                ORDER BY start_date ASC
                LIMIT 1
            """
            transition = self.db.execute_query(query, (today.strftime('%Y-%m-%d'),), fetch_one=True)
            
            if not transition:
                return None
            
            # Calculate days until transition
            transition_date = datetime.datetime.strptime(transition['start_date'], '%Y-%m-%d').date()
            days_until = (transition_date - today).days
            
            # Check if we should notify (14 days before)
            if days_until <= 14:
                # Mark as notified
                update_query = """
                    UPDATE seasonal_transitions
                    SET notification_sent = 1
                    WHERE transition_id = ?
                """
                self.db.execute_query(update_query, (transition['transition_id'],))
                
                # Get transition recommendations
                recommendations = self.get_transition_recommendations()
                
                return {
                    'season': transition['season'],
                    'start_date': transition['start_date'],
                    'days_until': days_until,
                    'recommendations': recommendations
                }
            
            return None
        except Exception as e:
            print(f"Error checking transition notification: {e}")
            return None


# Example usage
if __name__ == "__main__":
    helper = SeasonalTransitionHelper()
    
    # Set up seasonal transitions for current year
    helper.setup_seasonal_transitions()
    
    # Get current season
    current_season = helper.get_current_season()
    print(f"Current season: {current_season}")
    
    # Get upcoming season
    upcoming = helper.get_upcoming_season()
    print(f"Upcoming season: {upcoming['season']} starting on {upcoming['start_date']}")
    
    # Get transition recommendations
    recommendations = helper.get_transition_recommendations()
    print(f"Items to store: {len(recommendations['items_to_store'])}")
    print(f"Items to bring out: {len(recommendations['items_to_bring_out'])}")
    
    # Check for transition notification
    notification = helper.check_transition_notification()
    if notification:
        print(f"Transition notification: {notification['season']} is coming in {notification['days_until']} days")
