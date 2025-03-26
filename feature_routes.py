from flask import Blueprint, render_template, request, redirect, url_for, flash
from db.db_operations import DatabaseManager
from datetime import datetime, timedelta

def create_feature_routes(app, db):
    """
    Create routes for additional features like laundry tracker, outfit calendar, etc.
    
    Args:
        app: Flask application instance
        db: DatabaseManager instance
    """
    
    # ----- Laundry Tracker Routes -----
    
    @app.route('/laundry')
    def laundry_tracker():
        """Display the laundry tracker interface."""
        clean_items = db.get_clean_items()
        dirty_items = db.get_dirty_items()
        return render_template('features/laundry.html', clean_items=clean_items, dirty_items=dirty_items)
    
    @app.route('/laundry/mark_dirty/<int:item_id>', methods=['POST'])
    def mark_item_dirty(item_id):
        """Mark a clothing item as dirty."""
        success = db.mark_item_as_dirty(item_id)
        if success:
            flash('Item marked as dirty', 'success')
        else:
            flash('Failed to mark item as dirty', 'error')
        return redirect(url_for('laundry_tracker'))
    
    @app.route('/laundry/mark_clean/<int:item_id>', methods=['POST'])
    def mark_item_clean(item_id):
        """Mark a clothing item as clean."""
        success = db.mark_item_as_clean(item_id)
        if success:
            flash('Item marked as clean', 'success')
        else:
            flash('Failed to mark item as clean', 'error')
        return redirect(url_for('laundry_tracker'))
    
    # ----- Outfit Calendar Routes -----
    
    @app.route('/calendar')
    def outfit_calendar():
        """Display the outfit calendar interface."""
        # Get upcoming outfits for the next 14 days
        upcoming_outfits = db.get_upcoming_outfits(14)
        
        # Create a date range for the next 14 days
        today = datetime.now().date()
        date_range = [(today + timedelta(days=i)).strftime('%Y-%m-%d') for i in range(14)]
        
        # Create a dictionary of dates to outfits
        calendar_data = {}
        for date in date_range:
            calendar_data[date] = None
        
        for entry in upcoming_outfits:
            calendar_data[entry['date']] = entry
        
        # Get all outfits for scheduling
        all_outfits = db.get_all_outfits()
        
        return render_template('features/calendar.html', 
                              calendar_data=calendar_data, 
                              date_range=date_range, 
                              all_outfits=all_outfits)
    
    @app.route('/calendar/schedule', methods=['POST'])
    def schedule_outfit():
        """Schedule an outfit for a specific date."""
        outfit_id = request.form.get('outfit_id')
        date = request.form.get('date')
        notes = request.form.get('notes')
        
        if not outfit_id or not date:
            flash('Outfit and date are required', 'error')
            return redirect(url_for('outfit_calendar'))
        
        success = db.schedule_outfit(outfit_id, date, notes)
        if success:
            flash(f'Outfit scheduled for {date}', 'success')
        else:
            flash('Failed to schedule outfit', 'error')
        
        return redirect(url_for('outfit_calendar'))
    
    @app.route('/calendar/wear/<int:outfit_id>', methods=['POST'])
    def record_outfit_worn(outfit_id):
        """Record that an outfit was worn today."""
        date = request.form.get('date') or datetime.now().strftime('%Y-%m-%d')
        
        success = db.record_outfit_as_worn(outfit_id, date)
        if success:
            flash('Outfit recorded as worn', 'success')
        else:
            flash('Failed to record outfit as worn', 'error')
        
        return redirect(url_for('outfit_calendar'))
    
    # ----- Outfit Statistics Routes -----
    
    @app.route('/statistics')
    def outfit_statistics():
        """Display outfit statistics."""
        most_worn_outfits = db.get_most_worn_outfits(10)
        most_worn_items = db.get_most_worn_items(10)
        orphaned_items = db.get_orphaned_items(10)
        
        return render_template('features/statistics.html', 
                              most_worn_outfits=most_worn_outfits, 
                              most_worn_items=most_worn_items, 
                              orphaned_items=orphaned_items)
    
    # ----- Seasonal Transition Routes -----
    
    @app.route('/seasonal')
    def seasonal_transition():
        """Display seasonal wardrobe transition helper."""
        seasons = ['Spring', 'Summer', 'Fall', 'Winter']
        current_season = request.args.get('current_season', 'Winter')
        upcoming_season = request.args.get('upcoming_season', 'Spring')
        
        if current_season not in seasons or upcoming_season not in seasons:
            flash('Invalid season selection', 'error')
            return redirect(url_for('seasonal_transition'))
        
        items_to_store = db.get_items_to_store(current_season, upcoming_season)
        items_to_bring_out = db.get_items_to_bring_out(current_season, upcoming_season)
        
        return render_template('features/seasonal.html', 
                              seasons=seasons,
                              current_season=current_season, 
                              upcoming_season=upcoming_season,
                              items_to_store=items_to_store, 
                              items_to_bring_out=items_to_bring_out)
    
    # ----- Color Palette Analysis Routes -----
    
    @app.route('/colors')
    def color_palette():
        """Display color palette analysis."""
        color_distribution = db.get_color_distribution()
        
        # Define winter color palette
        winter_colors = ['Black', 'White', 'Navy', 'Royal Blue', 'Purple', 'Emerald', 'Ruby Red', 'Pink', 'Silver']
        
        # Get items by color
        items_by_color = {}
        for color_data in color_distribution:
            color = color_data['color']
            items = db.get_items_by_color(color)
            items_by_color[color] = items
        
        return render_template('features/colors.html', 
                              color_distribution=color_distribution,
                              items_by_color=items_by_color,
                              winter_colors=winter_colors)
