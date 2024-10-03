from flask import Flask, render_template, request, redirect, url_for, flash
import json
import bcrypt

app = Flask(__name__)
app.secret_key = 'supersecretkey'

### Load users from a JSON file
def load_users():
    try:
        with open("users.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

### Save users to a JSON file
def save_users(users):
    with open("users.json", "w", encoding="utf-8") as f:
        json.dump(users, f, indent=4)

### Helper functions
def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def check_password(password, hashed):
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

# In-memory bubbles for simplicity
bubbles = []

### Routes ###
@app.route('/')
def index():
    return render_template('index.html')

### User Registration and Login ###
@app.route('/register', methods=['POST'])
def register():
    username = request.form['username']
    password = request.form['password']
    users = load_users()
    
    if username in users:
        flash("Username already exists. Try a different one!", "error")
    else:
        users[username] = hash_password(password)
        save_users(users)
        flash(f"Welcome to Bubbl.ai, {username}!", "success")
    
    return redirect(url_for('index'))

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    users = load_users()

    if username in users and check_password(password, users[username]):
        flash(f"Welcome back, {username}!", "success")
        return redirect(url_for('main_menu', user=username))
    else:
        flash("Invalid login. Please try again.", "error")
        return redirect(url_for('index'))

### Main Menu ###
@app.route('/main_menu/<user>')
def main_menu(user):
    return render_template('main_menu.html', user=user)

### Creative Self Mode ###
@app.route('/creative_self_mode/<user>', methods=['GET', 'POST'])
def creative_self_mode(user):
    if request.method == 'POST':
        content = request.form['content']
        category = request.form.get('category', 'Uncategorized')
        bubbles.append({"user": user, "content": content, "category": category})
        flash("Bubble created successfully!", "success")
    
    return render_template('creative_self_mode.html', user=user)

### Explore Bubbles ###
@app.route('/explore_bubbles/<user>', methods=['GET', 'POST'])
def explore_bubbles(user):
    query = request.form.get('query', '')
    filtered_bubbles = [b for b in bubbles if query.lower() in b['content'].lower()]
    
    return render_template('explore_bubbles.html', user=user, bubbles=filtered_bubbles)

### Developer Mode ###
@app.route('/developer_mode/<user>', methods=['GET', 'POST'])
def developer_mode(user):
    if request.method == 'POST':
        if 'insert_json' in request.form:
            # Simulate inserting bubbles from a JSON file
            flash("Bubbles from JSON inserted!", "success")
        elif 'pop_all' in request.form:
            # Simulate popping all bubbles
            bubbles.clear()
            flash("All bubbles popped!", "success")
    
    return render_template('developer_mode.html', user=user)

### Profile Lookup Mode ###
@app.route('/profile_lookup/<user>', methods=['GET', 'POST'])
def profile_lookup(user):
    username = request.form.get('username', '')
    user_bubbles = [b for b in bubbles if b['user'] == username]

    return render_template('profile_lookup.html', user=user, user_bubbles=user_bubbles)

if __name__ == '__main__':
    app.run(debug=True)
