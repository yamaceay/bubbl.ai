from flask import Flask, render_template, request, redirect, url_for, session, flash
import bcrypt
import json
from lib import Handler, connect_weaviate_client
import os

app = Flask(__name__)
app.secret_key = 'super_secret_key'  # Replace with an actual secret key in production

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

# Use before_request to ensure the handler is initialized before each request
@app.before_request
def ensure_handler_initialized():
    initialize_handler()

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
                flash("🎉 You've successfully registered! 🎉", "success")
                return redirect(url_for('index'))
            else:
                flash("Username already exists. Try again! 😬", "error")
        elif action == 'login':
            if username in users and check_password(password, users[username]):
                session['user'] = username
                flash("🎉 Welcome back! 🎉", "success")
                return redirect(url_for('menu'))
            else:
                flash("Invalid username or password. 😬", "error")
    return render_template('login.html')

# Main Menu
@app.route('/menu')
def menu():
    if 'user' not in session:
        return redirect(url_for('index'))
    return render_template('menu.html')

# Creative Self Mode
@app.route('/creative_self', methods=['GET', 'POST'])
def creative_self():
    if 'user' not in session:
        return redirect(url_for('index'))

    if request.method == 'POST':
        if 'remove_bubble' in request.form:  # Handle bubble removal
            uuid = request.form['bubble_id']
            success = handler.remove_bubble(uuid)
            if success:
                flash(f"✨ Bubble with ID {uuid} has been successfully popped! 🎉", "success")
            else:
                flash(f"😕 Could not find or remove the bubble with ID {uuid}. It may have floated away. 🧐", "error")
        else:  # Handle bubble creation
            content = request.form['content']
            category = request.form['category']
            bubble = [{"content": content, "user": session['user'], "category": category}]
            result = handler.insert_bubbles(bubble)
            if result:
                flash(f"✨ Your bubble has been blown with ID(s): {result}! 🎉", "success")
            else:
                flash("Uh-oh! Something went wrong. Try again! 🌬️", "error")

    return render_template('creative_mode.html')

# Explore Bubbles
@app.route('/explore', methods=['GET', 'POST'])
def explore():
    if 'user' not in session:
        return redirect(url_for('index'))

    bubbles = None
    query = ""
    limit = 5  # Default limit (number of bubbles per page)
    offset = request.args.get('offset', 0, type=int)  # Default offset is 0 (start from the beginning)
    limit = request.args.get('limit', limit, type=int)  # Allow custom limit via URL parameter
    query = request.args.get('query', "")  # Persist the search query across pages
    has_more = True  # Default to True

    if request.method == 'POST':  # When the user submits a new query
        query = request.form['query']
        limit = int(request.form['limit'])
        if not query.strip():
            flash("Search query cannot be empty!", "error")
            return redirect(url_for('explore'))
        offset = 0  # Reset to the first page on new search
        return redirect(url_for('explore', query=query, offset=offset, limit=limit))  # Redirect to maintain the query and pagination in the URL

    # Fetch bubbles based on query, offset, and limit
    if query:
        try:
            bubbles = handler.search_bubbles(query, limit, offset)
        except ValueError as e:
            flash(str(e), "error")
            return redirect(url_for('explore'))

    # Determine if there are more bubbles for the "Next" page
    next_offset = offset + limit
    if query:
        has_more = handler.search_bubbles(query, 1, next_offset)  # Check if more bubbles exist beyond current limit

    return render_template('explore.html', bubbles=bubbles, query=query, offset=offset, limit=limit, has_more=has_more)

# Developer Mode
@app.route('/developer', methods=['GET', 'POST'])
def developer_mode():
    if 'user' not in session:
        return redirect(url_for('index'))

    if request.method == 'POST':
        if 'pop_all' in request.form:  # Handle the logic for popping all bubbles
            handler.remove_all_bubbles()
            flash("💥 Poof! All the bubbles are gone! Fresh air ahead! 🫧", "success")
        elif 'insert_bubbles' in request.form:  # Handle the logic for inserting bubbles from JSON
            json_file = request.form['json_file']
            try:
                with open(json_file, "r", encoding="utf-8") as f:
                    json_data = json.load(f)
                result = handler.insert_bubbles_from_json(json_data)
                if result:
                    flash(f"✨ Bubbles successfully blown! Bubble IDs: {result} 🎉", "success")
                else:
                    flash("Something went wrong. Try again! 🌬️", "error")
            except FileNotFoundError:
                flash("File not found. 🚫", "error")
    return render_template('developer_mode.html')

# Profile Lookup Mode
# Profile Lookup Mode
@app.route('/profile_lookup', methods=['GET', 'POST'])
def profile_lookup():
    if 'user' not in session:
        return redirect(url_for('index'))

    profile = None
    query = ""
    limit = 5  # Default limit (number of bubbles per page)
    offset = request.args.get('offset', 0, type=int)  # Default offset is 0 (start from the beginning)
    limit = request.args.get('limit', limit, type=int)  # Allow custom limit via URL parameter
    user_name = request.args.get('user_name', "")  # Persist the user name across pages
    has_more = True  # Default to True

    if request.method == 'POST':  # When the user submits a new query for profile lookup
        user_name = request.form['user_name']
        limit = int(request.form['limit'])
        if not user_name.strip():
            flash("Username cannot be empty!", "error")
            return redirect(url_for('profile_lookup'))
        offset = 0  # Reset to the first page on new search
        return redirect(url_for('profile_lookup', user_name=user_name, offset=offset, limit=limit))  # Redirect to maintain the user and pagination in the URL

    # Fetch user profile bubbles based on user_name, offset, and limit
    if user_name:
        try:
            profile = handler.query_user_profile(user_name, limit, offset)
        except ValueError as e:
            flash(str(e), "error")
            return redirect(url_for('profile_lookup'))

    # Determine if there are more bubbles for the "Next" page
    next_offset = offset + limit
    if user_name:
        has_more = handler.query_user_profile(user_name, 1, next_offset)  # Check if more bubbles exist beyond current limit

    return render_template('profile_lookup.html', profile=profile, user_name=user_name, offset=offset, limit=limit, has_more=has_more)

# Logout
@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
