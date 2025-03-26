#!/usr/bin/env python3
"""
Integration module for the Clothing Database System.
This module integrates all the additional features into the main application.
"""

from flask import Blueprint, request, jsonify, render_template
from modules.laundry_tracker import LaundryTracker
from modules.outfit_calendar import OutfitCalendar
from modules.seasonal_transition import SeasonalTransitionHelper
from modules.outfit_statistics import OutfitStatistics
from modules.color_palette import ColorPaletteAnalyzer

def create_feature_routes(app, db):
    """
    Create routes for all additional features.
    
    Args:
        app: Flask application instance
        db: Database manager instance
    """
    # Initialize feature modules
    laundry_tracker = LaundryTracker(db)
    outfit_calendar = OutfitCalendar(db)
    seasonal_helper = SeasonalTransitionHelper(db)
    outfit_stats = OutfitStatistics(db)
    color_analyzer = ColorPaletteAnalyzer(db)
    
    # Create a blueprint for feature routes
    features = Blueprint('features', __name__)
    
    # ----- Laundry Tracker Routes -----
    
    @features.route('/laundry/status/<int:item_id>', methods=['GET'])
    def get_laundry_status(item_id):
        """Get the laundry status of a clothing item."""
        status = laundry_tracker.get_item_status(item_id)
        return jsonify({'status': status})
    
    @features.route('/laundry/mark_dirty/<int:item_id>', methods=['POST'])
    def mark_item_dirty(item_id):
        """Mark a clothing item as dirty."""
        success = laundry_tracker.mark_as_dirty(item_id)
        return jsonify({'success': success})
    
    @features.route('/laundry/mark_clean/<int:item_id>', methods=['POST'])
    def mark_item_clean(item_id):
        """Mark a clothing item as clean."""
        success = laundry_tracker.mark_as_clean(item_id)
        return jsonify({'success': success})
    
    @features.route('/laundry/stats', methods=['GET'])
    def get_laundry_stats():
        """Get laundry statistics."""
        stats = laundry_tracker.get_laundry_statistics()
        return jsonify(stats)
    
    @features.route('/laundry/dirty_items', methods=['GET'])
    def get_dirty_items():
        """Get all dirty clothing items."""
        items = laundry_tracker.get_dirty_items()
        return jsonify({'items': items})
    
    # ----- Outfit Calendar Routes -----
    
    @features.route('/calendar/schedule', methods=['POST'])
    def schedule_outfit():
        """Schedule an outfit for a specific date."""
        data = request.json
        outfit_id = data.get('outfit_id')
        date = data.get('date')
        notes = data.get('notes')
        
        calendar_id = outfit_calendar.schedule_outfit(outfit_id, date, notes)
        
        if calendar_id:
            return jsonify({'success': True, 'calendar_id': calendar_id})
        else:
            return jsonify({'success': False, 'message': 'Failed to schedule outfit'})
    
    @features.route('/calendar/date/<string:date>', methods=['GET'])
    def get_outfit_for_date(date):
        """Get the scheduled outfit for a specific date."""
        outfit = outfit_calendar.get_outfit_for_date(date)
        
        if outfit:
            return jsonify({'success': True, 'outfit': outfit})
        else:
            return jsonify({'success': False, 'message': 'No outfit scheduled for this date'})
    
    @features.route('/calendar/week/<string:start_date>', methods=['GET'])
    def get_outfits_for_week(start_date):
        """Get all scheduled outfits for a week."""
        outfits = outfit_calendar.get_outfits_for_week(start_date)
        return jsonify({'outfits': outfits})
    
    @features.route('/calendar/today', methods=['GET'])
    def get_today_outfit():
        """Get the scheduled outfit for today."""
        outfit = outfit_calendar.get_today_outfit()
        
        if outfit:
            return jsonify({'success': True, 'outfit': outfit})
        else:
            return jsonify({'success': False, 'message': 'No outfit scheduled for today'})
    
    @features.route('/calendar/upcoming', methods=['GET'])
    def get_upcoming_outfits():
        """Get upcoming scheduled outfits."""
        days = request.args.get('days', default=7, type=int)
        outfits = outfit_calendar.get_upcoming_outfits(days)
        return jsonify({'outfits': outfits})
    
    # ----- Seasonal Transition Routes -----
    
    @features.route('/seasonal/current', methods=['GET'])
    def get_current_season():
        """Get the current season."""
        season = seasonal_helper.get_current_season()
        return jsonify({'season': season})
    
    @features.route('/seasonal/upcoming', methods=['GET'])
    def get_upcoming_season():
        """Get the upcoming season."""
        season = seasonal_helper.get_upcoming_season()
        return jsonify(season)
    
    @features.route('/seasonal/recommendations', methods=['GET'])
    def get_transition_recommendations():
        """Get recommendations for seasonal wardrobe transition."""
        recommendations = seasonal_helper.get_transition_recommendations()
        return jsonify(recommendations)
    
    @features.route('/seasonal/check_notification', methods=['GET'])
    def check_transition_notification():
        """Check if a transition notification should be sent."""
        notification = seasonal_helper.check_transition_notification()
        
        if notification:
            return jsonify({'success': True, 'notification': notification})
        else:
            return jsonify({'success': False, 'message': 'No transition notification needed'})
    
    # ----- Outfit Statistics Routes -----
    
    @features.route('/stats/record_wear', methods=['POST'])
    def record_outfit_wear():
        """Record that an outfit was worn."""
        data = request.json
        outfit_id = data.get('outfit_id')
        wear_date = data.get('wear_date')
        rating = data.get('rating')
        notes = data.get('notes')
        
        stat_id = outfit_stats.record_outfit_wear(outfit_id, wear_date, rating, notes)
        
        if stat_id:
            return jsonify({'success': True, 'stat_id': stat_id})
        else:
            return jsonify({'success': False, 'message': 'Failed to record outfit wear'})
    
    @features.route('/stats/outfit/<int:outfit_id>', methods=['GET'])
    def get_outfit_wear_history(outfit_id):
        """Get the wear history for a specific outfit."""
        history = outfit_stats.get_outfit_wear_history(outfit_id)
        return jsonify({'history': history})
    
    @features.route('/stats/item/<int:item_id>', methods=['GET'])
    def get_item_wear_history(item_id):
        """Get the wear history for a specific item."""
        history = outfit_stats.get_item_wear_history(item_id)
        return jsonify({'history': history})
    
    @features.route('/stats/most_worn_outfits', methods=['GET'])
    def get_most_worn_outfits():
        """Get the most frequently worn outfits."""
        limit = request.args.get('limit', default=10, type=int)
        outfits = outfit_stats.get_most_worn_outfits(limit)
        return jsonify({'outfits': outfits})
    
    @features.route('/stats/most_worn_items', methods=['GET'])
    def get_most_worn_items():
        """Get the most frequently worn items."""
        limit = request.args.get('limit', default=10, type=int)
        items = outfit_stats.get_most_worn_items(limit)
        return jsonify({'items': items})
    
    @features.route('/stats/least_worn_items', methods=['GET'])
    def get_least_worn_items():
        """Get the least frequently worn items."""
        limit = request.args.get('limit', default=10, type=int)
        items = outfit_stats.get_least_worn_items(limit)
        return jsonify({'items': items})
    
    @features.route('/stats/summary', methods=['GET'])
    def get_outfit_statistics_summary():
        """Get a summary of outfit statistics."""
        summary = outfit_stats.get_outfit_statistics_summary()
        return jsonify(summary)
    
    # ----- Color Palette Routes -----
    
    @features.route('/color/season', methods=['GET'])
    def get_user_color_season():
        """Get the user's personal color season."""
        season = color_analyzer.get_user_color_season()
        return jsonify({'season': season})
    
    @features.route('/color/season', methods=['POST'])
    def set_user_color_season():
        """Set the user's personal color season."""
        data = request.json
        season = data.get('season')
        
        success = color_analyzer.set_user_color_season(season)
        
        if success:
            return jsonify({'success': True, 'season': season})
        else:
            return jsonify({'success': False, 'message': 'Failed to set color season'})
    
    @features.route('/color/season_info', methods=['GET'])
    def get_color_season_info():
        """Get information about a color season."""
        season = request.args.get('season')
        info = color_analyzer.get_color_season_info(season)
        
        if info:
            return jsonify({'success': True, 'info': info})
        else:
            return jsonify({'success': False, 'message': 'Invalid color season'})
    
    @features.route('/color/item/<int:item_id>', methods=['GET'])
    def analyze_item_color_compatibility(item_id):
        """Analyze how well a clothing item's color matches the user's color season."""
        analysis = color_analyzer.analyze_item_color_compatibility(item_id)
        
        if analysis:
            return jsonify({'success': True, 'analysis': analysis})
        else:
            return jsonify({'success': False, 'message': 'Failed to analyze item'})
    
    @features.route('/color/outfit/<int:outfit_id>', methods=['GET'])
    def analyze_outfit_color_harmony(outfit_id):
        """Analyze the color harmony of an outfit."""
        analysis = color_analyzer.analyze_outfit_color_harmony(outfit_id)
        
        if analysis:
            return jsonify({'success': True, 'analysis': analysis})
        else:
            return jsonify({'success': False, 'message': 'Failed to analyze outfit'})
    
    @features.route('/color/wardrobe', methods=['GET'])
    def get_wardrobe_color_analysis():
        """Analyze the color distribution of the entire wardrobe."""
        analysis = color_analyzer.get_wardrobe_color_analysis()
        
        if analysis:
            return jsonify({'success': True, 'analysis': analysis})
        else:
            return jsonify({'success': False, 'message': 'Failed to analyze wardrobe'})
    
    # Register the blueprint with the app
    app.register_blueprint(features, url_prefix='/api/features')
    
    # Create feature pages
    
    @app.route('/laundry')
    def laundry_page():
        """Display laundry tracker page."""
        return render_template('features/laundry.html')
    
    @app.route('/calendar')
    def calendar_page():
        """Display outfit calendar page."""
        return render_template('features/calendar.html')
    
    @app.route('/seasonal')
    def seasonal_page():
        """Display seasonal transition page."""
        return render_template('features/seasonal.html')
    
    @app.route('/statistics')
    def statistics_page():
        """Display outfit statistics page."""
        return render_template('features/statistics.html')
    
    @app.route('/color')
    def color_page():
        """Display color palette analysis page."""
        return render_template('features/color.html')
    
    return app
