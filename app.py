from flask import Flask, render_template, request, redirect, url_for, session, flash
import bcrypt
import json
from lib import Handler, connect_weaviate_client
import os
from functools import wraps

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'super_secret_key')  # Use environment variable for security

# Initialize the handler once (Singleton Pattern)
handler = None

def initialize_handler():
    global handler
    if handler is None:
        client = connect_weaviate_client()
        if client:
            user = session.get('user', None)
            handler = Handler(client, user)
            handler.create_bubble_schema()

# Ensure the handler is initialized before each request
@app.before_request
def ensure_handler_initialized():
    initialize_handler()
    if 'user' in session and handler:
        handler.user = session['user']  # Dynamically update the user in the handler

# Helper function for Flash Messages
def flash_message(message, category="info"):
    flash(message, category)

# Helper function to manage pagination parameters
def handle_pagination(request, limit=5):
    offset = request.args.get('offset', 0, type=int)
    limit = request.args.get('limit', limit, type=int)
    return limit, offset

# Custom Login Required Decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            flash_message("You need to log in first!", "error")
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

# Load users
def load_users():
    if os.path.exists("users.json"):
        with open("users.json", "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

# Save users
def save_users(users):
    with open("users.json", "w", encoding="utf-8") as f:
        json.dump(users, f, indent=4)

# Hash password
def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

# Check password
def check_password(password, hashed):
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

# Home Page (Login/Register)
@app.route('/', methods=['GET', 'POST'])
def index():
    users = load_users()
    if request.method == 'POST':
        action = request.form['action']
        username = request.form['username']
        password = request.form['password']

        if action == 'register':
            if username not in users:
                users[username] = hash_password(password)
                save_users(users)
                flash_message("🎉 You've successfully registered!", "success")
                return redirect(url_for('index'))
            else:
                flash_message("Username already exists. Try again! 😬", "error")
        elif action == 'login':
            if username in users and check_password(password, users[username]):
                session['user'] = username
                flash_message("🎉 Welcome back! 🎉", "success")
                return redirect(url_for('menu'))
            else:
                flash_message("Invalid username or password. 😬", "error")
    return render_template('login.html')

# Main Menu
@app.route('/menu')
@login_required
def menu():
    return render_template('menu.html')

@app.route('/creative_self', methods=['GET', 'POST'])
@login_required
def creative_self():
    limit = 5  # Fixed limit of 5 bubbles per page
    offset = request.args.get('offset', 0, type=int)  # Default offset is 0 (start from the beginning)
    user_name = session['user']  # Get the logged-in user's name
    has_more = True  # Default to True
    bubbles = None

    # Fetch the user's bubbles for display
    try:
        bubbles = handler.query_user_profile(user_name, "", "", limit, offset)
    except ValueError as e:
        flash_message(str(e), "error")
        return redirect(url_for('menu'))

    # Handle bubble removal
    if request.method == 'POST' and 'remove_bubble' in request.form:
        bubble_id = request.form['bubble_id']  # Fetch the bubble_id from the form
        success = handler.remove_bubble(bubble_id)
        if success:
            flash_message(f"✨ Bubble with ID {bubble_id} has been successfully popped! 🎉", "success")
        else:
            flash_message(f"😕 Could not find or remove the bubble with ID {bubble_id}. It may have floated away. 🧐", "error")
        return redirect(url_for('creative_self'))

    # Handle bubble creation (writing new bubbles)
    if request.method == 'POST' and 'create_bubble' in request.form:
        content = request.form['content'].strip()
        category = request.form.get('category', '').strip()  # Category is optional
        if not content:
            flash_message("Content cannot be empty! 🧐", "error")
        else:
            bubble = [{"content": content, "user": user_name, "category": category}]
            result = handler.insert_bubbles(bubble)
            if result:
                flash_message(f"✨ Your bubble has been blown with ID(s): {result}! 🎉", "success")
            else:
                flash_message("Uh-oh! Something went wrong while creating the bubble. Try again! 🌬️", "error")
        return redirect(url_for('creative_self'))

    # Determine if there are more bubbles for pagination
    next_offset = offset + limit
    has_more = handler.query_user_profile(user_name, "", "", 1, next_offset)

    return render_template('creative_mode.html', bubbles=bubbles, offset=offset, limit=limit, has_more=has_more)

# Explore Bubbles
@app.route('/explore', methods=['GET', 'POST'])
@login_required
def explore():
    limit = 5  # Fixed limit of 5 bubbles per page
    offset = request.args.get('offset', 0, type=int)  # Default offset is 0 (start from the beginning)
    query = request.args.get('query', "")
    query_category = request.args.get('query_category', "")

    if request.method == 'POST':  # When the user submits a new query
        query = request.form['query']
        query_category = request.form['query_category']
        return redirect(url_for('explore', query=query, query_category=query_category, limit=limit, offset=0))  # Reset to first page on new search

    # Fetch bubbles based on query, offset, and fixed limit
    bubbles = None
    try:
        bubbles = handler.search_bubbles(query, query_category, limit, offset)
    except ValueError as e:
        flash_message(str(e), "error")
        return redirect(url_for('explore'))

    # Determine if there are more bubbles for the "Next" page
    next_offset = offset + limit
    has_more = handler.search_bubbles(query, query_category, 1, next_offset) if query or query_category else True

    return render_template('explore.html', bubbles=bubbles, query=query, query_category=query_category, offset=offset, limit=limit, has_more=has_more)

# Find Like-Minded Bubblers
@app.route('/find_like_minded', methods=['GET', 'POST'])
@login_required
def find_like_minded():
    user_name = session['user']  # Get the logged-in user's name
    query_text = ""
    query_category = ""
    similar_users = None
    limit = 5  # Fixed limit of 5 similar users per page
    offset = request.args.get('offset', 0, type=int)  # Default offset for pagination
    has_more = False

    if request.method == 'POST':
        # Handle search submission
        query_text = request.form['query_text'].strip()
        query_category = request.form['query_category'].strip()

    # Call the handler to find similar users based on the query
    try:
        similar_users = handler.search_users_by_profile(query_text, query_category, limit, offset)
    except ValueError as e:
        flash_message(str(e), "error")
        return redirect(url_for('find_like_minded'))

    # If the result is None, it means the current user has no bubbles yet.
    if similar_users is None:
        flash_message("You have no bubbles yet to summarize! Create some bubbles first.", "info")

    # Check if there are more users beyond the current limit
    next_offset = offset + limit
    has_more = handler.search_users_by_profile(query_text, query_category, 1, next_offset)

    return render_template('find_like_minded.html', query_text=query_text, query_category=query_category, similar_users=similar_users, offset=offset, limit=limit, has_more=has_more)


# Developer Mode
@app.route('/developer', methods=['GET', 'POST'])
@login_required
def developer_mode():
    if request.method == 'POST':
        if 'pop_all' in request.form:  # Handle the logic for popping all bubbles
            handler.remove_all_bubbles(confirmation="yes")
            flash_message("💥 Poof! All the bubbles are gone! Fresh air ahead! 🫧", "success")
        elif 'insert_bubbles' in request.form:  # Handle the logic for inserting bubbles from JSON
            json_file = request.form['json_file']
            try:
                with open(json_file, "r", encoding="utf-8") as f:
                    json_data = json.load(f)
                result = handler.insert_bubbles_from_json(json_data)
                if result:
                    flash_message(f"✨ Bubbles successfully blown! Bubble IDs: {result} 🎉", "success")
                else:
                    flash_message("Something went wrong. Try again! 🌬️", "error")
            except FileNotFoundError:
                flash_message("File not found. 🚫", "error")
    return render_template('developer_mode.html')

# Profile Lookup Mode with Filters and Pagination
@app.route('/profile_lookup', methods=['GET', 'POST'])
@login_required
def profile_lookup():
    limit = 5  # Fixed limit of 5 bubbles per page
    offset = request.args.get('offset', 0, type=int)  # Default offset is 0 (start from the beginning)
    query_text = request.args.get('query_text', "")  # Persist the query text across pages
    query_category = request.args.get('query_category', "")  # Persist the category filter across pages
    user_name = request.args.get('user_name', "")  # Persist the user name across pages
    has_more = True  # Default to True
    profile = None

    if request.method == 'POST':  # When the user submits new query or category filters
        user_name = request.form['user_name']
        query_text = request.form['query_text'].strip()
        query_category = request.form['query_category'].strip()
        if not user_name.strip():
            flash_message("Username cannot be empty!", "error")
            return redirect(url_for('profile_lookup'))
        return redirect(url_for('profile_lookup', user_name=user_name, query_text=query_text, query_category=query_category, offset=0))

    # Fetch user profile bubbles based on user_name, query text, category filter, offset, and fixed limit
    if user_name:
        try:
            profile = handler.query_user_profile(user_name, query_text, query_category, limit, offset)
        except ValueError as e:
            flash_message(str(e), "error")
            return redirect(url_for('profile_lookup'))

    # Determine if there are more bubbles for the "Next" page
    next_offset = offset + limit
    has_more = handler.query_user_profile(user_name, query_text, query_category, 1, next_offset) if user_name else False

    return render_template('profile_lookup.html', profile=profile, user_name=user_name, query_text=query_text, query_category=query_category, offset=offset, has_more=has_more)

# Logout
@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
