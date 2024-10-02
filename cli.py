import json
from src import connect_weaviate_client, handle_action

def bubbly_print(message, emoji="💬"):
    """
    Prints a message with an accompanying emoji to provide a playful tone.

    Args:
        message (str): The message to print.
        emoji (str): The emoji to prepend to the message (default is "💬").
    """
    print(f"{emoji} {message}")

def print_menu():
    """
    Displays the main menu for the Bubbl.ai CLI, providing options for different actions.
    """
    print("\n🎈 What bubbly adventure would you like to embark on?")
    print("1. 🎨 Enter Creative Self Mode (Shape Your Profile)")
    print("2. 🔍 Explore Bubbles (Discover Thought Bubbles)")
    print("3. 🔍 Find Like-minded Bubblers (Find Fellow Bubblers by Similarity)")
    print("4. 👤 Enter Profile Lookup Mode (Peek at User Profiles)")
    print("5. 👨‍💻 Enter Developer Mode (Tinker with All Bubbles)")
    print("6. 🚪 Drift Away from Bubbl.ai (Exit)")
    print("\n" + "-"*40 + "\n")

def developer_mode(client, user):
    """
    Provides options for managing all bubbles in Developer Mode, including inserting bubbles
    from a JSON file or removing all bubbles.

    Args:
        client: Weaviate client instance.
        user (str): The current user.
    """
    while True:
        print(f"\n👨‍💻 Developer Mode activated for {user}!")
        print("1. 📂 Blow Bubbles from a JSON File")
        print("2. 🚨 Pop ALL the Bubbles (Careful!)")
        print("3. 🚪 Drift out of Developer Mode")
        choice = input("Choose your developer action: ")

        if choice == "1":
            insert_bubbles_from_json(client, user)
        elif choice == "2":
            pop_all_bubbles(client, user)
        elif choice == "3":
            bubbly_print(f"Exiting Developer Mode for {user}. 🌬️", "👋")
            break
        else:
            bubbly_print("Oops! That wasn't a valid option. Try again! 💫", "🤔")

def insert_bubbles_from_json(client, user):
    """
    Inserts bubbles from a JSON file into the Bubbl.ai platform.

    Args:
        client: Weaviate client instance.
        user (str): The current user.
    """
    bubbly_print("Time to breathe life into some bubbles from a JSON file! 🎈")
    json_file = validate_file_path("Enter the path to your bubbly JSON file: ")
    try:
        with open(json_file, "r", encoding="utf-8") as f:
            json_data = json.load(f)
        result = handle_action(client, user, "insert_bubbles_from_json", json_data=json_data)
        if result:
            bubbly_print(f"✨ Bubbles successfully blown! Bubble IDs: {result} 🎉")
        else:
            bubbly_print("Uh-oh! Something went wrong. Those bubbles didn’t float. Try again! 🌬️", "😬")
    except FileNotFoundError:
        bubbly_print("Oops! That file flew away! Double-check your path and try again! 🚫", "😬")

def pop_all_bubbles(client, user):
    """
    Removes all bubbles from the Bubbl.ai platform after user confirmation.

    Args:
        client: Weaviate client instance.
        user (str): The current user.
    """
    bubbly_print("⚠️ Are you **really** sure you want to pop ALL the bubbles? Once they're gone, there's no bringing them back! ⚠️")
    confirmation = input("Type 'yes' if you're absolutely certain: ")
    if confirmation.lower() == 'yes':
        success = handle_action(client, user, "remove_all_bubbles")
        if success:
            bubbly_print("💥 Poof! All the bubbles are gone! Fresh air ahead! 🫧")
        else:
            bubbly_print("Something went wrong! Those bubbles are still floating around. 🌈", "😬")
    else:
        bubbly_print("Phew! The bubbles are safe for now. 😊", "😌")

def user_profile_mode(client, user_name, user):
    """
    Enters the Profile Lookup Mode, allowing the current user to view and query another user's bubbles.

    Args:
        client: Weaviate client instance.
        user_name (str): The username of the profile being viewed.
        user (str): The current user.
    """
    bubbly_print(f"You're now floating through the profile view for user: {user_name} 🧑‍💻", "👤")

    query_text = ""
    query_category = ""
    top_k = 5

    while True:
        print("\nWhat would you like to do in this bubble?")
        print(f"1. ✍️ Update your search query text (Current: '{query_text or 'Not Set'}')")
        print(f"2. 🏷️ Update your category filter (Current: '{query_category or 'Not Set'}')")
        print(f"3. 🔢 Set the number of bubbles to retrieve (Current: '{top_k}')")
        print("4. 🚀 Send the search bubbles into action!")
        print("5. 🚪 Float away from Profile Mode")

        profile_choice = input("👉 Choose an option (1-5): ")

        if profile_choice == "1":
            query_text = input("Enter your search query text (Press ENTER to clear): ").strip()
        elif profile_choice == "2":
            query_category = input("Enter the category to filter by (Press ENTER to clear): ").strip()
        elif profile_choice == "3":
            top_k = validate_number_input("How many bubbles do you want to retrieve? (Enter a number or press ENTER to keep the current value): ", top_k)
        elif profile_choice == "4":
            perform_query(client, user_name, user, query_text, query_category, top_k)
        elif profile_choice == "5":
            bubbly_print(f"Exiting profile view for user: {user_name} 🚪", "👋")
            break
        else:
            bubbly_print("Oops! That wasn’t a valid option. Try again! 💫", "🤔")

def perform_query(client, user_name, user, query_text, query_category, top_k):
    """
    Performs a search query for bubbles related to a user profile with optional filters.

    Args:
        client: Weaviate client instance.
        user_name (str): The username of the profile being queried.
        user (str): The current user.
        query_text (str): The text to query.
        query_category (str): The category to filter by.
        top_k (int): Number of results to retrieve.
    """
    bubbly_print(f"Searching for bubbles with query: '{query_text or 'None'}', category: '{query_category or 'None'}', showing the top {top_k} results.", "🚀")
    profile = handle_action(client, user, action="query_user_profile", user_name=user_name, query_text=query_text, query_category=query_category, top_k=top_k)
    display_profile(profile)

def display_profile(profile):
    """
    Displays the user profile and bubbles retrieved by a search query.

    Args:
        profile (dict): The profile information and bubbles to display.
    """
    if 'message' in profile:
        bubbly_print(profile['message'], "😕")
    else:
        bubbly_print(f"Profile of {profile['user']} 🌟")
        print(f"Total bubbles blown: {profile['total_bubbles']}")
        print("Recent bubbles:")
        for bubble in profile['bubbles']:
            print(f"💬 {bubble['content']} (Category: {bubble['category']})")

def validate_number_input(prompt, default=None):
    """
    Validates and returns a numeric input from the user, with an optional default value.

    Args:
        prompt (str): The prompt to display to the user.
        default (int, optional): The default value if no input is given.

    Returns:
        int: The validated number input.
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

    Args:
        prompt (str): The prompt to display to the user.

    Returns:
        str: The validated file path.
    """
    while True:
        file_path = input(prompt)
        try:
            with open(file_path, "r", encoding="utf-8"):
                return file_path
        except FileNotFoundError:
            bubbly_print("Oops! That file isn't floating anywhere nearby. Check your path again! 🚫", "😬")

def export_bubbles(client, user):
    """
    Exports all bubbles created by the user into a JSON file.

    Args:
        client: Weaviate client instance.
        user (str): The current user.
    """
    bubbles = handle_action(client, user, "get_bubbles")
    if bubbles:
        file_name = f"{user}_bubbles.json"
        with open(file_name, 'w', encoding='utf-8') as f:
            json.dump(bubbles, f, indent=4)
        bubbly_print(f"✨ All your bubbles have been saved to {file_name} 🎉", "💾")
    else:
        bubbly_print("Oops! It looks like you don’t have any bubbles to export yet. Time to start bubbling! 😕")

def creative_self_mode(client, user):
    """
    Provides options to the user for managing their own bubbles, including inserting and removing bubbles, 
    and querying their own profile.

    Args:
        client: Weaviate client instance.
        user (str): The current user.
    """
    while True:
        print(f"\n🎨 Welcome to Creative Self Mode, {user}! Time to shape your bubble universe! ✨")
        print("1. 💭 Blow a new bubble")
        print("2. 🗑️ Pop one of your bubbles")
        print("3. 🔍 Peek at your profile bubbles")
        print("4. 🚪 Float away from Creative Self Mode")
        choice = input("Choose an option: ")

        if choice == "1":
            insert_bubble(client, user)
        elif choice == "2":
            remove_bubble(client, user)
        elif choice == "3":
            query_user_profile(client, user)
        elif choice == "4":
            bubbly_print(f"Floating away from Creative Self Mode for {user}. 🌬️", "👋")
            break
        else:
            bubbly_print("Oops! That wasn't a valid option. Give it another try! 💫", "🤔")

def insert_bubble(client, user):
    """
    Allows the user to create and insert a new bubble into the Bubbl.ai platform.

    Args:
        client: Weaviate client instance.
        user (str): The current user.
    """
    bubbly_print("Let’s blow a fresh new bubble! 🎈")
    content = input("What’s on your mind? Type it out and I’ll turn it into a bubble: ")
    category_suggestions = ["Technology", "Life", "Fun"]
    print(f"Here are some popular categories: {', '.join(category_suggestions)}")
    category = input("How would you categorize this bubble? (Press ENTER to skip): ")
    bubble = [{"content": content, "user": user, "category": category}]
    result = handle_action(client, user, action="insert_bubbles", bubble_data=bubble)
    if result:
        bubbly_print(f"✨ Your bubble has been blown with ID(s): {result}! 🎉", "🫧")
    else:
        bubbly_print("Uh-oh! Something went wrong. Your bubble didn’t float this time. Try again! 🌬️", "😬")

def remove_bubble(client, user):
    """
    Allows the user to remove one of their bubbles by specifying the UUID.

    Args:
        client: Weaviate client instance.
        user (str): The current user.
    """
    bubbly_print("Time to pop one of your bubbles! 🗑️")
    uuid = input("Enter the UUID of the bubble you want to pop: ")
    success = handle_action(client, user, action="remove_bubble", uuid=uuid)
    if success:
        bubbly_print(f"✨ Bubble with UUID {uuid} has been successfully popped! 🎉", "🎈")
    else:
        bubbly_print(f"Oops! Couldn’t find that bubble with UUID {uuid}. It might’ve floated away. 🧐")

def query_user_profile(client, user):
    """
    Queries and displays the profile and bubbles of the current user.

    Args:
        client: Weaviate client instance.
        user (str): The current user.
    """
    bubbly_print(f"Peeking into your profile bubbles, {user}. Let’s see what you’ve been bubbling about! 🔍", "👤")
    profile = handle_action(client, user, "query_user_profile")
    display_profile(profile)

def explore_bubbles(client, user):
    """
    Allows the user to explore and search for bubbles created by others based on a query.

    Args:
        client: Weaviate client instance.
        user (str): The current user.
    """
    bubbly_print("Ready to explore the bubble universe? Let’s search for some thought bubbles! 🔍")
    query_text = input("Enter your search query: ")
    top_k = validate_number_input("How many bubbles would you like to see? (Enter a number): ")
    bubbles = handle_action(client, user, action="search_bubbles", query_text=query_text, top_k=top_k)
    if bubbles:
        print("🫧 Found these thought bubbles:")
        for bubble in bubbles:
            print(f"💬 {bubble['content']} (User: {bubble['user']}, Category: {bubble['category']})")
    else:
        bubbly_print("No bubbles found. Try adjusting your search query! 🌈")

def find_like_minded_bubblers(client, user):
    """
    Searches for other users with similar bubbles and thought patterns based on a search query.

    Args:
        client: Weaviate client instance.
        user (str): The current user.
    """
    bubbly_print("Let’s find some fellow Bubblers who think like you! 🫂")
    query_text = input("Enter your search query: ")
    top_k = validate_number_input("How many bubbles would you like to compare with others? (Enter a number): ")
    top_k_user = validate_number_input("How many bubbles from your profile should we use for comparison? (Enter a number): ")
    users = handle_action(client, user, action="search_users_by_query", query_text=query_text, top_k=top_k, top_k_user=top_k_user)
    if users:
        print("🎈 Here are some Bubblers who share your thoughts:")
        for user_data in users:
            print(f"👤 User: {user_data['user']}, Similarity: {user_data['similarity'] * 100:.2f}%")
    else:
        bubbly_print("No similar Bubblers found. Try another search! 🌟")

def enter_profile_lookup_mode(client, user):
    """
    Prompts the user to enter a username and view another user's profile bubbles.

    Args:
        client: Weaviate client instance.
        user (str): The current user.
    """
    bubbly_print("Let’s peek into someone else’s bubble universe! 👤")
    user_name = input("Enter the username of the Bubblr you'd like to explore: ")
    user_profile_mode(client, user_name, user)

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
        client = connect_weaviate_client()
        if not client:
            bubbly_print("Oops! Couldn’t connect to the Bubbl.ai server. Try again later! 😕", "😕")
            return

        try:
            handle_action(client, user, "create_bubble_schema")
            main_menu(client, user)
        finally:
            client.close()

def load_users():
    """
    Loads the list of registered users from the 'users.json' file.

    Returns:
        dict: The loaded user data.
    """
    try:
        with open("users.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def authenticate_user(users):
    """
    Authenticates the user by either registering a new user or logging in an existing user.

    Args:
        users (dict): The dictionary containing all registered users.

    Returns:
        str: The authenticated username.
    """
    while True:
        print("\n👋 Ready to dive into Bubbl.ai? Please sign up or log in first!",
              "\n1. 📝 Register and start bubbling",
              "\n2. 🔑 Log in and resume your bubble journey",
              "\n3. 🚨 Deregister your Bubbl account",
              "\n4. 🚪 Drift away (Exit Bubbl.ai)",
              "\n" + "-"*40 + "\n")
        choice = input("👉 What would you like to do? (1-4): ")
        
        if choice == "1":
            user = register_user(users)
        elif choice == "2":
            user = login_user(users)
        elif choice == "3":
            deregister_user(users, user)
        elif choice == "4":
            bubbly_print("Thanks for visiting Bubbl.ai! Until next time, keep your thoughts floating! ✨", "👋")
            exit(0)
        else:   
            bubbly_print("Oops! That wasn’t a valid choice. Let’s try again! 💫", "🤔")

        if user:
            return user

def register_user(users):
    """
    Registers a new user and adds them to the 'users.json' file.

    Args:
        users (dict): The dictionary containing all registered users.

    Returns:
        str: The newly registered username.
    """
    user_name = input("Enter your bubbly username: ")
    password = input("Enter your bubbly password: ")
    result = handle_action(None, user_name, "register_user", users=users, password=password)
    if result and 'users' in result:
        bubbly_print("🎉 Welcome to the bubble universe! You’re officially a Bubblr! 🎉", "🎈")
        users = result.get('users')
        with open("users.json", "w", encoding="utf-8") as f:
            json.dump(users, f, indent=4)
        return user_name
    else:
        bubbly_print("Oops! Something went wrong. Try registering again! 😬")
        return None

def login_user(users):
    """
    Logs in an existing user by validating their username and password.

    Args:
        users (dict): The dictionary containing all registered users.

    Returns:
        str: The authenticated username.
    """
    user_name = input("Enter your bubbly username: ")
    password = input("Enter your bubbly password: ")
    result = handle_action(None, user_name, "login_user", users=users, password=password)
    if result:
        bubbly_print("🎉 Welcome back! Let’s get your bubbles floating again! 🎉", "🎈")
        return user_name
    else:
        bubbly_print("Oops! Couldn’t log in. Let’s try again! 😬")
        return None

def deregister_user(users, user):
    """
    Deregisters the current user from the system and removes them from 'users.json'.

    Args:
        users (dict): The dictionary containing all registered users.
        user (str): The current user.
    """
    if user is None:
        bubbly_print("Please log in before attempting to deregister. 😬")
        return
    result = handle_action(None, user, action="deregister_user", users=users)
    if result and 'users' in result:
        bubbly_print("🎉 You’ve successfully popped your account. Come back to bubble anytime! 🎉", "🎈")
        users = result.get('users')
        with open("users.json", "w", encoding="utf-8") as f:
            json.dump(users, f, indent=4)
    else:
        bubbly_print("Oops! Something went wrong during deregistration. Try again? 😬")

def main_menu(client, user):
    """
    Displays the main menu and handles the user’s selection of actions.

    Args:
        client: Weaviate client instance.
        user (str): The current user.
    """
    print_menu()
    while True:
        choice = input("👉 Make your bubbly choice (1-6): ")

        if not choice.isdigit() or not 1 <= int(choice) <= 6:
            bubbly_print("Oops! That wasn’t a valid option. Let’s try again! 💫", "🤔")
            continue

        if choice == "1":
            bubbly_print("🎨 Welcome to Creative Self Mode! 🎨", "🎨")
            creative_self_mode(client, user)
        elif choice == "2":
            explore_bubbles(client, user)
        elif choice == "3":
            find_like_minded_bubblers(client, user)
        elif choice == "4":
            enter_profile_lookup_mode(client, user)
        elif choice == "5":
            developer_mode(client, user)
        elif choice == "6":
            bubbly_print("Thanks for visiting Bubbl.ai! Until next time, keep your thoughts floating! ✨", "👋")
            break

        print_menu()

if __name__ == "__main__":
    main()
