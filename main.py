import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
from sklearn.metrics.pairwise import cosine_similarity
from src import connect_weaviate_client, query_most_relevant_bubbles, insert_bubbles, remove_bubble, \
    embed_text_with_openai, compute_user_similarity, embed_user_summaries, group_bubbles_by_user, summarize_user_content

# Initialize Dash app
app = dash.Dash(__name__, external_stylesheets=["https://codepen.io/chriddyp/pen/bWLwgP.css"])

# Connect to Weaviate client
client = connect_weaviate_client()

# Basic user management (in-memory)
users_db = {"testuser": "password123"}  # Simulate a user database
current_user = None  # Placeholder for logged-in user


# Custom CSS for elliptical bubbles
bubble_style = {
    "display": "inline-block",
    "padding": "20px",
    "margin": "10px",
    "border": "2px solid #ccc",
    "border-radius": "50%",  # Creates an elliptical bubble
    "width": "150px",
    "height": "100px",
    "text-align": "center",
    "vertical-align": "middle",
    "background-color": "#f9f9f9",
}

# App layout
app.layout = html.Div([
    html.H1("Welcome to Bubbl.ai", style={'textAlign': 'center'}),

    html.Div(id='login-section', style={'display': 'block'}),  # Placeholder for login/register
    html.Div(id='page-content', style={'marginTop': '20px'}),

    # Options at the bottom
    html.Div([
        html.Button("💭 Insert Bubble", id="insert-bubble-btn", style={'marginRight': '10px'}),
        html.Button("🔍 Search Bubbles", id="search-bubble-btn", style={'marginRight': '10px'}),
        html.Button("🔍 Search Users by Similarity", id="search-user-btn", style={'marginRight': '10px'}),
        html.Button("🗑️ Remove a Bubble", id="remove-bubble-btn", style={'marginRight': '10px'}),
    ], style={'textAlign': 'center', 'padding': '20px', 'position': 'fixed', 'bottom': '0', 'width': '100%'})
])

# Display login or register form
@app.callback(
    Output('login-section', 'children'),
    [Input('page-content', 'children')]
)
def display_login(_):
    if current_user is None:
        return html.Div([
            dcc.Input(id='username', type='text', placeholder="Enter Username"),
            dcc.Input(id='password', type='password', placeholder="Enter Password"),
            html.Button('Login', id='login-button', n_clicks=0),
            html.Button('Register', id='register-button', n_clicks=0),
            html.Div(id='login-output', style={'marginTop': '10px'})
        ], style={'textAlign': 'center', 'padding': '20px'})
    return html.Div(f"Welcome, {current_user}!", style={'textAlign': 'center', 'marginTop': '10px'})

# Callback for login and registration
@app.callback(
    Output('login-output', 'children'),
    [Input('login-button', 'n_clicks'), Input('register-button', 'n_clicks')],
    [State('username', 'value'), State('password', 'value')]
)
def login_register(login_clicks, register_clicks, username, password):
    global current_user, users_db
    if username and password:
        if login_clicks > 0:
            # Handle login
            if username in users_db and users_db[username] == password:
                current_user = username
                return f"Successfully logged in as {username}."
            return "Invalid username or password."
        elif register_clicks > 0:
            # Handle registration
            if username in users_db:
                return "Username already exists."
            users_db[username] = password
            return f"User {username} registered successfully."
    return ""

# Display content based on selected option
@app.callback(
    Output('page-content', 'children'),
    [Input('insert-bubble-btn', 'n_clicks'),
     Input('search-bubble-btn', 'n_clicks'),
     Input('search-user-btn', 'n_clicks'),
     Input('remove-bubble-btn', 'n_clicks')]
)
def display_page(insert_clicks, search_clicks, user_search_clicks, remove_clicks):
    if insert_clicks:
        return insert_bubble_layout()
    elif search_clicks:
        return search_bubble_layout()
    elif user_search_clicks:
        return search_user_layout()
    elif remove_clicks:
        return remove_bubble_layout()
    return html.Div()

# Layout for inserting a bubble
def insert_bubble_layout():
    return html.Div([
        html.H3("Insert a New Bubble"),
        dcc.Input(id="bubble-content", type="text", placeholder="Enter bubble content", style={'width': '50%'}),
        dcc.Input(id="bubble-category", type="text", placeholder="Enter bubble category", style={'width': '50%', 'marginTop': '10px'}),
        html.Button("Insert Bubble", id="submit-bubble-btn", style={'marginTop': '10px'}),
        html.Div(id="insert-bubble-output", style={'marginTop': '20px'})
    ])

@app.callback(
    Output('insert-bubble-output', 'children'),
    [Input('submit-bubble-btn', 'n_clicks')],
    [State('bubble-content', 'value'), State('bubble-category', 'value')]
)
def insert_bubble(n_clicks, content, category):
    if n_clicks and content and category:
        if current_user:
            bubble = [{"content": content, "user": current_user, "category": category}]
            response = insert_bubbles(client, bubble)
            if response:
                return f"Bubble inserted successfully: {response}"
        else:
            return "Please log in to insert a bubble."
    return "Enter content and category to insert a bubble."

# Layout for searching bubbles by similarity
def search_bubble_layout():
    return html.Div([
        html.H3("Search Bubbles by Similarity"),
        dcc.Input(id="search-query", type="text", placeholder="Enter search query", style={'width': '50%'}),
        dcc.Slider(id="result-slider", min=1, max=20, step=1, value=5, marks={i: str(i) for i in range(1, 21)}),
        html.Button("Search Bubbles", id="search-bubble-submit-btn", style={'marginTop': '10px'}),
        html.Div(id="search-bubble-output", style={'marginTop': '20px'})
    ])

@app.callback(
    Output('search-bubble-output', 'children'),
    [Input('search-bubble-submit-btn', 'n_clicks')],
    [State('search-query', 'value'), State('result-slider', 'value')]
)
def search_bubbles(n_clicks, query_text, k):
    if n_clicks and query_text:
        bubbles = query_most_relevant_bubbles(client, query_text, k)
        if bubbles:
            # Display bubbles as elliptic items
            return html.Div([html.Div(f"{bubble['content']} (User: {bubble['user']}, Category: {bubble['category']})", style=bubble_style) for bubble in bubbles])
    return "Enter a search query."

# Layout for searching users by similarity
def search_user_layout():
    return html.Div([
        html.H3("Search Users by Similarity"),
        dcc.Input(id="user-search-query", type="text", placeholder="Enter search query", style={'width': '50%'}),
        dcc.Slider(id="user-result-slider", min=1, max=10, step=1, value=5, marks={i: str(i) for i in range(1, 11)}),
        html.Button("Search Users", id="user-search-submit-btn", style={'marginTop': '10px'}),
        html.Div(id="search-user-output", style={'marginTop': '20px'})
    ])

@app.callback(
    Output('search-user-output', 'children'),
    [Input('user-search-submit-btn', 'n_clicks')],
    [State('user-search-query', 'value'), State('user-result-slider', 'value')]
)
def search_users(n_clicks, query_text, k):
    if n_clicks and query_text:
        bubbles = query_most_relevant_bubbles(client, query_text, k)
        user_bubbles = group_bubbles_by_user(bubbles)
        user_summaries = summarize_user_content(user_bubbles)
        query_embedding = embed_text_with_openai(query_text)
        user_embeddings = embed_user_summaries(user_summaries)
        ranked_users = compute_user_similarity(user_embeddings, query_embedding)
        if ranked_users:
            return html.Div([html.Div(f"User: {user['user']}, Similarity: {user['similarity'] * 100:.2f}%", style=bubble_style) for user in ranked_users])
    return "Enter a search query."

# Layout for removing a bubble
def remove_bubble_layout():
    return html.Div([
        html.H3("Remove a Bubble"),
        dcc.Input(id="bubble-uuid", type="text", placeholder="Enter Bubble UUID", style={'width': '50%'}),
        html.Button("Remove Bubble", id="remove-bubble-submit-btn", style={'marginTop': '10px'}),
        html.Div(id="remove-bubble-output", style={'marginTop': '20px'})
    ])

@app.callback(
    Output('remove-bubble-output', 'children'),
    [Input('remove-bubble-submit-btn', 'n_clicks')],
    [State('bubble-uuid', 'value')]
)
def remove_bubble(n_clicks, uuid):
    if n_clicks and uuid:
        response = remove_bubble(client, uuid)
        if response:
            return f"Bubble with UUID {uuid} removed successfully."
    return "Enter a valid UUID."

# Start the Dash app (use app.run_server() instead of app.run() in Dash 2.0+)
if __name__ == '__main__':
    app.run(debug=True)
