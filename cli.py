import json
import sys
import termios
import tty
import time
import bcrypt
from lib import Handler, connect_weaviate_client

### Helper Functions ###
def bubbly_print(message, emoji="💬"):
    """
    Prints a message with an accompanying emoji to provide a playful tone.
    """
    print(f"{emoji} {message}")


def prompt_choice(options, message="Choose an option: ", error_message="Oops! That wasn’t a valid option. Try again!"):
    """
    Prompts the user to select an option from a list of choices.
    """
    print("\n".join([f"{i}. {option}" for i, option in enumerate(options, 1)]))
    while True:
        choice = input(message)
        if choice.isdigit() and 1 <= int(choice) <= len(options):
            return int(choice)
        else:
            bubbly_print(error_message, "🤔")


def validate_number_input(prompt, default=None):
    """
    Validates and returns a numeric input from the user, with an optional default value.
    """
    while True:
        try:
            value = input(prompt)
            if value.strip() == "" and default is not None:
                return default
            return int(value)
        except ValueError:
            bubbly_print("Oops! That wasn’t a valid number. Let’s try again! 💫", "🤔")


def validate_file_path(prompt):
    """
    Validates the file path input from the user to ensure the file exists.
    """
    while True:
        file_path = input(prompt)
        try:
            with open(file_path, "r", encoding="utf-8"):
                return file_path
        except FileNotFoundError:
            bubbly_print("Oops! That file isn't floating anywhere nearby. Check your path again! 🚫", "😬")


def hash_password(password):
    """
    Hashes a user's password using bcrypt.
    """
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')


def check_password(password, hashed):
    """
    Verifies a password against a hashed password.
    """
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

def custom_getpass(prompt="Password: "):
    """
    Custom getpass function to display * for each character typed.
    """
    print(prompt, end='', flush=True)
    password = ""
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        while True:
            ch = sys.stdin.read(1)
            if ch == '\n' or ch == '\r':
                break
            elif ch == '\x7f':  # Handle backspace
                if len(password) > 0:
                    password = password[:-1]
                    sys.stdout.write('\b \b')
                    sys.stdout.flush()
            else:
                password += ch
                sys.stdout.write('*')
                sys.stdout.flush()
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    print()  # Move to the next line
    return password

### Connection with Retry ###
def connect_weaviate_with_retries(retries=3, delay=2):
    """
    Tries to connect to the Weaviate client with retry logic.
    """
    for attempt in range(retries):
        client = connect_weaviate_client()
        if client:
            return client
        bubbly_print(f"Attempt {attempt + 1} failed, retrying in {delay} seconds...", "🤔")
        time.sleep(delay)
    return None

def developer_mode(handler):
    """
    Provides options for managing all bubbles in Developer Mode.
    """
    while True:
        print(f"\n👨‍💻 Developer Mode activated for {handler.user}!")
        options = [
            "📂 Blow Bubbles from a JSON File",
            "🚨 Pop ALL the Bubbles (Careful!)",
            "🚪 Drift out of Developer Mode"
        ]
        choice = prompt_choice(options, "Choose your developer action: ")

        if choice == 1:
            insert_bubbles_from_json(handler)
        elif choice == 2:
            pop_all_bubbles(handler)
        elif choice == 3:
            bubbly_print(f"Exiting Developer Mode for {handler.user}. 🌬️", "👋")
            break


def insert_bubbles_from_json(handler):
    """
    Inserts bubbles from a JSON file into the Bubbl.ai platform.
    """
    bubbly_print("Time to breathe life into some bubbles from a JSON file! 🎈")
    json_file = validate_file_path("Enter the path to your bubbly JSON file: ")
    try:
        with open(json_file, "r", encoding="utf-8") as f:
            json_data = json.load(f)
        result = handler.insert_bubbles_from_json(json_data)
        if result:
            bubbly_print(f"✨ Bubbles successfully blown! Bubble IDs: {result} 🎉")
        else:
            bubbly_print("Uh-oh! Something went wrong. Those bubbles didn’t float. Try again! 🌬️", "😬")
    except (FileNotFoundError, PermissionError) as e:
        bubbly_print(f"Oops! File error: {e}. Please check and try again! 🚫", "😬")


def pop_all_bubbles(handler):
    """
    Removes all bubbles from the Bubbl.ai platform after user confirmation.
    """
    bubbly_print("⚠️ Are you **really** sure you want to pop ALL the bubbles? Once they're gone, there's no bringing them back! ⚠️")
    confirmation = input("Type 'yes' if you're absolutely certain: ").lower()
    if confirmation == 'yes':
        success = handler.remove_all_bubbles(confirmation)
        if success:
            bubbly_print("💥 Poof! All the bubbles are gone! Fresh air ahead! 🫧")
        else:
            bubbly_print("Something went wrong! Those bubbles are still floating around. 🌈", "😬")
    else:
        bubbly_print("Phew! The bubbles are safe for now. 😊", "😌")


def creative_self_mode(handler):
    """
    Provides options to the user for managing their own bubbles.
    """
    while True:
        print(f"\n🎨 Welcome to Creative Self Mode, {handler.user}! Time to shape your bubble universe! ✨")
        options = [
            "💭 Blow a new bubble",
            "🗑️ Pop one of your bubbles",
            "🔍 Peek at your profile bubbles",
            "🚪 Float away from Creative Self Mode"
        ]
        choice = prompt_choice(options)

        if choice == 1:
            insert_bubble(handler)
        elif choice == 2:
            remove_bubble(handler)
        elif choice == 3:
            query_user_profile(handler)
        elif choice == 4:
            bubbly_print(f"Floating away from Creative Self Mode for {handler.user}. 🌬️", "👋")
            break

def query_user_profile(handler):
    """
    Provides options to the user for querying their own profile bubbles.
    """
    offset = 0
    limit = 5
    while True:
        bubbly_print(f"Peeking into your profile bubbles, {handler.user}. Let’s see what you’ve been bubbling about! 🔍", "👤")
        profile = handler.query_user_profile(handler.user, limit, offset)
        display_profile(profile)
        if input("Do you want to see more bubbles? (y/n): ").lower() != 'y':
            break
        offset += limit

def insert_bubble(handler):
    """
    Allows the user to create and insert a new bubble into the Bubbl.ai platform.
    """
    bubbly_print("Let’s blow a fresh new bubble! 🎈")
    content = input("What’s on your mind? Type it out and I’ll turn it into a bubble: ")
    category_suggestions = ["Technology", "Life", "Fun"]
    print(f"Here are some popular categories: {', '.join(category_suggestions)}")
    category = input("How would you categorize this bubble? (Press ENTER to skip): ")
    bubble = [{"content": content, "user": handler.user, "category": category}]
    result = handler.insert_bubble(bubble)
    if result:
        bubbly_print(f"✨ Your bubble has been blown with ID(s): {result}! 🎉", "🫧")
    else:
        bubbly_print("Uh-oh! Something went wrong. Your bubble didn’t float this time. Try again! 🌬️", "😬")


def remove_bubble(handler):
    """
    Allows the user to remove one of their bubbles by specifying the UUID.
    """
    bubbly_print("Time to pop one of your bubbles! 🗑️")
    uuid = input("Enter the UUID of the bubble you want to pop: ")
    success = handler.remove_bubble(uuid)
    if success:
        bubbly_print(f"✨ Bubble with UUID {uuid} has been successfully popped! 🎉", "🎈")
    else:
        bubbly_print(f"Oops! Couldn’t find that bubble with UUID {uuid}. It might’ve floated away. 🧐")


def explore_bubbles(handler):
    """
    Allows the user to explore and search for bubbles created by others based on a query.
    """
    bubbly_print("Ready to explore the bubble universe? Let’s search for some thought bubbles! 🔍")
    query_text = input("Enter your search query: ")
    page_size = validate_number_input("How many bubbles per page? (Enter a number): ")

    offset = 0
    while True:
        bubbles = handler.search_bubbles(query_text, page_size, offset)
        if bubbles:
            print("🫧 Found these thought bubbles:")
            for bubble in bubbles:
                print(f"💬 {bubble['content']} (User: {bubble['user']}, Category: {bubble['category']})")
        else:
            bubbly_print("No more bubbles found. 🌈")
            break

        next_page = input("Do you want to see more bubbles? (y/n): ").lower()
        if next_page == 'n':
            break
        offset += page_size


def find_like_minded_bubblers(handler):
    """
    Searches for other users with similar bubbles and thought patterns based on a search query.
    """
    limit = 50 # Number of bubbles to fetch for similarity comparison
    limit_user = 5 # Number of bubbles to fetch from the current user for comparison
    bubbly_print("Let’s find some fellow Bubblers who think like you! 🫂")
    query_text = input("Enter your search query: ")
    users_similarity = handler.search_users_by_profile(query_text, limit, limit_user)
    if users_similarity:
        print("🎈 Here are some Bubblers who share your thoughts:")
        for user_data in users_similarity:
            print(f"👤 User: {user_data['user']}, Similarity: {user_data['similarity'] * 100:.2f}%")
    else:
        bubbly_print("No similar Bubblers found. Try another search! 🌟")


def user_profile_mode(handler, user_name):
    """
    Enters the Profile Lookup Mode, allowing the current user to view and query another user's bubbles.
    """
    bubbly_print(f"You're now floating through the profile view for user: {user_name} 🧑‍💻", "👤")

    limit = 5
    offset = 0
    query_text = ""
    query_category = ""

    while True:
        print("\nWhat would you like to do in this bubble?")
        options = [
            f"✍️ Update your search query text (Current: '{query_text or 'Not Set'}')",
            f"🏷️ Update your category filter (Current: '{query_category or 'Not Set'}')",
            "🚀 Send the search bubbles into action!",
            "🚪 Float away from Profile Mode"
        ]
        profile_choice = prompt_choice(options)

        if profile_choice == 1:
            query_text = input("Enter your search query text (Press ENTER to clear): ").strip()
        elif profile_choice == 2:
            query_category = input("Enter the category to filter by (Press ENTER to clear): ").strip()
        elif profile_choice == 3:
            while True:
                perform_query(handler, user_name, query_text, query_category, limit, offset)
                page = input("Do you want to see more bubbles? (n for next, p for previous, any other key for no): ")
                if page == "n":
                    offset += limit
                elif page == "p":
                    offset -= limit
                else:
                    break
        elif profile_choice == 4:
            bubbly_print(f"Exiting profile view for user: {user_name} 🚪", "👋")
            break


def perform_query(handler, user_name, query_text, query_category, limit, offset):
    """
    Performs a search query for bubbles related to a user profile with optional filters.
    """
    bubbly_print(f"Searching for bubbles with query: '{query_text or 'None'}', category: '{query_category or 'None'}', showing the top {offset} - {offset + limit} results.", "🚀")
    profile = handler.query_user_profile(user_name, query_text, query_category, limit, offset)
    display_profile(profile)


def display_profile(profile):
    """
    Displays the user profile and bubbles retrieved by a search query.
    """
    if 'message' in profile:
        bubbly_print(profile['message'], "😕")
    else:
        bubbly_print(f"Profile of {profile['user']} 🌟")
        print(f"Total bubbles blown: {profile['total_bubbles']}")
        print("Recent bubbles:")
        for bubble in profile['bubbles']:
            print(f"💬 {bubble['content']} (Category: {bubble['category']})")


def enter_profile_lookup_mode(handler):
    """
    Prompts the user to enter a username and view another user's profile bubbles.
    """
    bubbly_print("Let’s peek into someone else’s bubble universe! 👤")
    user_name = input("Enter the username of the Bubblr you'd like to explore: ")
    user_profile_mode(handler, user_name)


### User Management ###
def load_users():
    """
    Loads the list of registered users from the 'users.json' file.
    """
    try:
        with open("users.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}


def authenticate_user(users):
    """
    Authenticates the user by either registering a new user or logging in an existing user.
    """
    while True:
        options = [
            "📝 Register and start bubbling",
            "🔑 Log in and resume your bubble journey",
            "🚨 Deregister your Bubbl account",
            "🚪 Drift away (Exit Bubbl.ai)"
        ]
        choice = prompt_choice(options, "👉 What would you like to do? (1-4): ")
        
        if choice == 1:
            user = register_user(users)
        elif choice == 2:
            user = login_user(users)
        elif choice == 3:
            deregister_user(users, user)
        elif choice == 4:
            bubbly_print("Thanks for visiting Bubbl.ai! Until next time, keep your thoughts floating! ✨", "👋")
            exit(0)

        if user:
            return user

def register_user(users):
    """
    Registers a new user and adds them to the 'users.json' file.
    """
    user_name = input("Enter your bubbly username: ")
    password = hash_password(custom_getpass("Enter your bubbly password: "))
    if user_name not in users:
        users[user_name] = password
        bubbly_print("🎉 Welcome to the bubble universe! You’re officially a Bubblr! 🎉", "🎈")
        with open("users.json", "w", encoding="utf-8") as f:
            json.dump(users, f, indent=4)
        return user_name
    else:
        bubbly_print("Oops! Something went wrong. Try registering again! 😬")
        return None


def login_user(users):
    """
    Logs in an existing user by validating their username and password.
    """
    user_name = input("Enter your bubbly username: ")
    password = custom_getpass("Enter your bubbly password: ")
    user_data = users.get(user_name)

    if user_data and check_password(password, users[user_name]):
        bubbly_print("🎉 Welcome back! Let’s get your bubbles floating again! 🎉", "🎈")
        return user_name
    else:
        bubbly_print("Oops! Couldn’t log in. Let’s try again! 😬")
        return None


def deregister_user(users, user):
    """
    Deregisters the current user from the system and removes them from 'users.json'.
    """
    if user is None:
        bubbly_print("Please log in before attempting to deregister. 😬")
        return
    if user in users:
        del users[user]
        bubbly_print("🎉 You’ve successfully popped your account. Come back to bubble anytime! 🎉", "🎈")
        with open("users.json", "w", encoding="utf-8") as f:
            json.dump(users, f, indent=4)
    else:
        bubbly_print("Oops! Something went wrong during deregistration. Try again? 😬")

def main_menu(handler):
    """
    Displays the main menu and handles the user’s selection of actions.
    """
    while True:
        options = [
            "🎨 Creative Self Mode (Shape Your Profile)",
            "🔍 Explore Bubbles (Discover Thought Bubbles)",
            "🔍 Find Like-minded Bubblers (Find Fellow Bubblers by Similarity)",
            "👤 Profile Lookup Mode (Peek at User Profiles)",
            "👨‍💻 Developer Mode (Tinker with All Bubbles)",
            "🚪 Drift Away from Bubbl.ai (Exit)"
        ]
        choice = prompt_choice(options)

        if choice == 1:
            bubbly_print("🎨 Welcome to Creative Self Mode! 🎨", "🎨")
            creative_self_mode(handler)
        elif choice == 2:
            explore_bubbles(handler)
        elif choice == 3:
            find_like_minded_bubblers(handler)
        elif choice == 4:
            enter_profile_lookup_mode(handler)
        elif choice == 5:
            developer_mode(handler)
        elif choice == 6:
            bubbly_print("Thanks for visiting Bubbl.ai! Until next time, keep your thoughts floating! ✨", "👋")
            break

### Main ###
def main():
    """
    Main function that initializes the Bubbl.ai CLI, manages user authentication, 
    and handles the main menu navigation.
    """
    bubbly_print("🌟 Welcome to Bubbl.ai, your floating universe of thoughts! 🌟", "✨")
    bubbly_print("Let’s start bubbling! Your ideas, musings, and reflections are waiting to float in the world of Bubbl.ai!", "💭")

    users = load_users()
    user = authenticate_user(users)

    if user:
        client = connect_weaviate_with_retries()
        if not client:
            bubbly_print("Oops! Couldn’t connect to the Bubbl.ai server. Try again later! 😕", "😕")
            return

        handler = Handler(client, user)
        try:
            handler.create_bubble_schema()
            main_menu(handler)
        finally:
            client.close()

if __name__ == "__main__":
    main()
