#!/usr/bin/env python3
"""
Flask web application for the Clothing Database System.
This script provides a web interface for managing clothing items, outfits, and tags.
"""

import os
import sqlite3
from datetime import datetime
import json
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, send_from_directory
from werkzeug.utils import secure_filename
from db.db_operations import DatabaseManager
from chatbot.chatbot_routes import add_generate_new_route
from feature_integration import create_feature_routes

# Initialize Flask application
app = Flask(__name__)
app.secret_key = 'clothing_database_secret_key'  # For flash messages and sessions

# Add the generate_new_outfit route
add_generate_new_route(app)

# Configure upload folder for photos
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "photos")
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure upload directories exist
os.makedirs(os.path.join(UPLOAD_FOLDER, "items"), exist_ok=True)
os.makedirs(os.path.join(UPLOAD_FOLDER, "outfits"), exist_ok=True)

# Initialize database manager
db = DatabaseManager()

def allowed_file(filename):
    """Check if the file has an allowed extension."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    """Render the home page."""
    return render_template('index.html')

# ----- Clothing Items Routes -----

@app.route('/items')
def items_list():
    """Display all clothing items."""
    items = db.get_all_clothing_items()
    return render_template('items/list.html', items=items)

@app.route('/items/filter', methods=['GET'])
def filter_items():
    """Filter clothing items by type."""
    item_type = request.args.get('type', 'All')
    
    if item_type == 'All':
        items = db.get_all_clothing_items()
    else:
        items = db.get_all_clothing_items(filters={'type': item_type})
    
    return render_template('items/list.html', items=items, selected_type=item_type)

@app.route('/items/new', methods=['GET'])
def new_item():
    """Display form to create a new clothing item."""
    return render_template('items/form.html', item=None)

@app.route('/items/<int:item_id>')
def view_item(item_id):
    """Display a specific clothing item."""
    item = db.get_clothing_item(item_id)
    if not item:
        flash('Item not found', 'error')
        return redirect(url_for('items_list'))
    
    # Get outfits that contain this item
    outfits = db.find_outfits_by_item(item_id)
    
    return render_template('items/view.html', item=item, outfits=outfits)

@app.route('/items/<int:item_id>/edit', methods=['GET'])
def edit_item(item_id):
    """Display form to edit a clothing item."""
    item = db.get_clothing_item(item_id)
    if not item:
        flash('Item not found', 'error')
        return redirect(url_for('items_list'))
    
    return render_template('items/form.html', item=item)

@app.route('/items/save', methods=['POST'])
def save_item():
    """Save a new or updated clothing item."""
    item_id = request.form.get('item_id')
    name = request.form.get('name')
    item_type = request.form.get('item_type') or request.form.get('type')
    color = request.form.get('color')
    brand = request.form.get('brand')
    size = request.form.get('size')
    material = request.form.get('material')
    season = request.form.get('season')
    occasion = request.form.get('occasion')
    notes = request.form.get('notes')
    
    # Validate required fields
    if not name or not item_type or not color:
        flash('Name, Type, and Color are required fields', 'error')
        return redirect(url_for('new_item' if not item_id else 'edit_item', item_id=item_id))
    
    # Prepare item data
    item_data = {
        'name': name,
        'item_type': item_type,  # Changed from 'type' to 'item_type'
        'color': color,
        'brand': brand or None,
        'size': size or None,
        'material': material or None,
        'season': season or None,
        'occasion': occasion or None,
        'notes': notes or None
    }
    
    try:
        if item_id:
            # Update existing item
            success = db.update_clothing_item(int(item_id), **item_data)
            if success:
                flash('Item updated successfully', 'success')
            else:
                flash('Failed to update item', 'error')
        else:
            # Add new item
            item_id = db.add_clothing_item(**item_data)
            if item_id:
                flash(f'Item added successfully with ID: {item_id}', 'success')
            else:
                flash('Failed to add item', 'error')
        
        # Handle photo upload
        if 'photo' in request.files:
            file = request.files['photo']
            if file and file.filename and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], "items", filename)
                file.save(file_path)
                db.add_photo_to_item(item_id, file_path)
        
        return redirect(url_for('view_item', item_id=item_id))
        
    except Exception as e:
        flash(f'An error occurred: {str(e)}', 'error')
        return redirect(url_for('items_list'))

@app.route('/items/<int:item_id>/delete', methods=['POST'])
def delete_item(item_id):
    """Delete a clothing item."""
    try:
        # Check if item is used in any outfits
        outfits = db.find_outfits_by_item(item_id)
        if outfits:
            outfit_names = ", ".join([outfit['name'] for outfit in outfits])
            flash(f'This item is used in the following outfits: {outfit_names}. Deleting this item will remove it from these outfits.', 'warning')
        
        # Delete the item
        success = db.delete_clothing_item(item_id)
        if success:
            flash('Item deleted successfully', 'success')
        else:
            flash('Failed to delete item', 'error')
        
        return redirect(url_for('items_list'))
        
    except Exception as e:
        flash(f'An error occurred: {str(e)}', 'error')
        return redirect(url_for('items_list'))

# ----- Outfits Routes -----

@app.route('/outfits')
def outfits_list():
    """Display all outfits."""
    outfits = db.get_all_outfits()
    return render_template('outfits/list.html', outfits=outfits)

@app.route('/outfits/new', methods=['GET'])
def new_outfit():
    """Display form to create a new outfit."""
    items = db.get_all_clothing_items()
    tags = db.get_all_tags()
    tag_categories = db.get_all_tag_categories()
    return render_template('outfits/form.html', outfit=None, items=items, tags=tags, tag_categories=tag_categories)

@app.route('/outfits/<int:outfit_id>')
def view_outfit(outfit_id):
    """Display a specific outfit."""
    outfit = db.get_outfit(outfit_id)
    if not outfit:
        flash('Outfit not found', 'error')
        return redirect(url_for('outfits_list'))
    
    return render_template('outfits/view.html', outfit=outfit)

@app.route('/outfits/<int:outfit_id>/edit', methods=['GET'])
def edit_outfit(outfit_id):
    """Display form to edit an outfit."""
    outfit = db.get_outfit(outfit_id)
    if not outfit:
        flash('Outfit not found', 'error')
        return redirect(url_for('outfits_list'))
    
    items = db.get_all_clothing_items()
    tags = db.get_all_tags()
    tag_categories = db.get_all_tag_categories()
    
    return render_template('outfits/form.html', outfit=outfit, items=items, tags=tags, tag_categories=tag_categories)

@app.route('/outfits/save', methods=['POST'])
def save_outfit():
    """Save a new or updated outfit."""
    outfit_id = request.form.get('outfit_id')
    name = request.form.get('name')
    description = request.form.get('description')
    rating = request.form.get('rating')
    
    # Get selected items and tags
    item_ids = request.form.getlist('item_ids')
    tag_ids = request.form.getlist('tag_ids')
    
    # Validate required fields
    if not name:
        flash('Name is a required field', 'error')
        return redirect(url_for('new_outfit' if not outfit_id else 'edit_outfit', outfit_id=outfit_id))
    
    try:
        if outfit_id:
            # Update existing outfit
            success = db.update_outfit(
                int(outfit_id),
                name=name,
                description=description,
                rating=int(rating) if rating and int(rating) > 0 else None
            )
            if success:
                flash('Outfit updated successfully', 'success')
            else:
                flash('Failed to update outfit', 'error')
        else:
            # Add new outfit
            outfit_id = db.add_outfit(
                name=name,
                description=description,
                rating=int(rating) if rating and int(rating) > 0 else None
            )
            if outfit_id:
                flash(f'Outfit added successfully with ID: {outfit_id}', 'success')
            else:
                flash('Failed to add outfit', 'error')
        
        if outfit_id:
            # Update items in outfit
            # First, get current outfit to find existing items
            outfit = db.get_outfit(outfit_id)
            
            # Remove items not in the new selection
            for item in outfit['items']:
                if str(item['item_id']) not in item_ids:
                    db.remove_item_from_outfit(outfit_id, item['item_id'])
            
            # Add new items
            for item_id in item_ids:
                if not any(item['item_id'] == int(item_id) for item in outfit['items']):
                    db.add_item_to_outfit(outfit_id, int(item_id))
            
            # Update tags
            # Remove tags not in the new selection
            for tag in outfit['tags']:
                if str(tag['tag_id']) not in tag_ids:
                    db.remove_tag_from_outfit(outfit_id, tag['tag_id'])
            
            # Add new tags
            for tag_id in tag_ids:
                if not any(tag['tag_id'] == int(tag_id) for tag in outfit['tags']):
                    db.add_tag_to_outfit(outfit_id, int(tag_id))
            
            # Handle photo upload
            if 'photo' in request.files:
                file = request.files['photo']
                if file and file.filename and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    file_path = os.path.join(app.config['UPLOAD_FOLDER'], "outfits", filename)
                    file.save(file_path)
                    db.add_photo_to_outfit(outfit_id, file_path)
        
        return redirect(url_for('view_outfit', outfit_id=outfit_id))
        
    except Exception as e:
        flash(f'An error occurred: {str(e)}', 'error')
        return redirect(url_for('outfits_list'))

@app.route('/outfits/<int:outfit_id>/delete', methods=['POST'])
def delete_outfit(outfit_id):
    """Delete an outfit."""
    try:
        # Delete the outfit
        success = db.delete_outfit(outfit_id)
        if success:
            flash('Outfit deleted successfully', 'success')
        else:
            flash('Failed to delete outfit', 'error')
        
        return redirect(url_for('outfits_list'))
        
    except Exception as e:
        flash(f'An error occurred: {str(e)}', 'error')
        return redirect(url_for('outfits_list'))

# ----- Search Routes -----

@app.route('/search')
def search_form():
    """Display search form."""
    items = db.get_all_clothing_items()
    tags = db.get_all_tags()
    return render_template('search/form.html', items=items, tags=tags)

@app.route('/search/results', methods=['GET'])
def search_results():
    """Display search results."""
    search_type = request.args.get('search_type')
    
    if search_type == 'item':
        item_id = request.args.get('item_id')
        if item_id:
            outfits = db.find_outfits_by_item(int(item_id))
        else:
            outfits = []
    elif search_type == 'name':
        query = request.args.get('query')
        outfits = db.search_outfits(query=query) if query else []
    elif search_type == 'tag':
        tag_id = request.args.get('tag_id')
        if tag_id:
            outfits = db.search_outfits(tag_ids=[int(tag_id)])
        else:
            outfits = []
    else:
        outfits = []
    
    return render_template('search/results.html', outfits=outfits, search_type=search_type)

# ----- Chatbot Routes -----

@app.route('/chatbot')
def chatbot():
    """Display chatbot interface."""
    return render_template('chatbot/interface.html')

@app.route('/chatbot/suggest', methods=['POST'])
def suggest_outfit():
    """Generate an outfit suggestion based on the message."""
    from chatbot.outfit_chatbot import OutfitChatbot
    
    # Initialize the chatbot if it doesn't exist in the session
    if 'chatbot' not in globals():
        global chatbot
        chatbot = OutfitChatbot(db)
    
    message = request.form.get('message', '').lower()
    
    # Process the message through the chatbot
    result = chatbot.process_message(message)
    
    return jsonify(result)

@app.route('/chatbot/save', methods=['POST'])
def save_suggested_outfit():
    """Save a suggested outfit to the database."""
    try:
        # Access the global chatbot instance
        if 'chatbot' not in globals():
            return jsonify({'success': False, 'message': 'No active chatbot session. Please refresh the page and try again.'})
        
        # Get the current outfit from the chatbot
        save_result = chatbot.save_current_outfit()
        if not save_result['success']:
            return jsonify(save_result)
        
        data = save_result['outfit']
        
        # Create a new outfit
        outfit_id = db.add_outfit(
            name=data['name'],
            description="Generated by Outfit Assistant"
        )
        
        if not outfit_id:
            return jsonify({'success': False, 'message': 'Failed to create outfit.'})
        
        # Add items to the outfit
        for item in data['items']:
            db.add_item_to_outfit(outfit_id, item['item_id'])
        
        # Add tags to the outfit
        tags = db.get_all_tags()
        
        # Add style tag if available
        if data['style']:
            style_tag = next((tag for tag in tags if tag['name'] == data['style']), None)
            if style_tag:
                db.add_tag_to_outfit(outfit_id, style_tag['tag_id'])
        
        # Add occasion tag if available
        if data['occasion']:
            occasion_tag = next((tag for tag in tags if tag['name'] == data['occasion']), None)
            if occasion_tag:
                db.add_tag_to_outfit(outfit_id, occasion_tag['tag_id'])
        
        # Add season tag if available
        if data['season']:
            season_tag = next((tag for tag in tags if tag['name'] == data['season']), None)
            if season_tag:
                db.add_tag_to_outfit(outfit_id, season_tag['tag_id'])
        
        return jsonify({
            'success': True, 
            'message': f"Outfit '{data['name']}' saved successfully!",
            'outfit_id': outfit_id
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'An error occurred: {str(e)}'})

# ----- Photo Routes -----

@app.route('/photos/<path:filename>')
def get_photo(filename):
    """Serve photos from the upload folder."""
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# ----- Main -----

# Initialize all additional features
create_feature_routes(app, db)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
