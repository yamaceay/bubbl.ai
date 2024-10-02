import json
from src import connect_weaviate_client, handle_action

def bubbly_print(message, emoji="💬"):
    print(f"{emoji} {message}")

def print_menu():
    print("\n🎈 What bubbly adventure would you like to embark on?")
    print("1. 💭 Blow a new Bubble (Insert a Bubble)")
    print("2. 🔍 Explore Bubbles (Search Bubbles)")
    print("3. 🔍 Find Like-minded Bubblers (Search Users by Similarity)")
    print("4. 🗑️  Pop a Bubble (Remove a Bubble)")
    print("5. 👤 Enter User Profile Mode (View User Profile)")
    print("6. 📂 Blow Bubbles from JSON (Insert Bubbles from a JSON file)")
    print("7. 🚨 Pop ALL the Bubbles (Remove All Bubbles with Confirmation)")
    print("8. 🚪 Exit Bubbl.ai")
    print("\n" + "-"*40 + "\n")
def user_profile_mode(client, user_name):
    """
    Enter into a mode where queries can be performed on a specific user's profile without re-entering the username.
    Allows setting and editing of filters before performing the query.
    """
    bubbly_print(f"You're now in the profile view mode for user: {user_name} 🧑‍💻", "👤")
    
    # Initialize default filters
    query_text = ""
    query_category = ""
    top_k = 5
    
    while True:
        # Provide options to set filters or perform the query
        print("\nWhat would you like to do?")
        print("1. ✍️ Edit search query text (Current: '{}')".format(query_text or "Not Set"))
        print("2. 🏷️ Edit category filter (Current: '{}')".format(query_category or "Not Set"))
        print("3. 🔢 Set number of results to retrieve (Current: '{}')".format(top_k))
        print("4. 🚀 Perform the query")
        print("5. 🚪 Exit profile mode")
        
        profile_choice = input("👉 Choose an option (1-5): ")

        if profile_choice == "1":
            # Edit search query text
            query_text = input("Enter your search query text (Press ENTER to clear): ")
            if not query_text.strip():
                query_text = ""

        elif profile_choice == "2":
            # Edit category filter
            query_category = input("Enter the category to filter by (Press ENTER to clear): ")
            if not query_category.strip():
                query_category = ""

        elif profile_choice == "3":
            # Set number of results (top_k)
            top_k_input = input("How many recent bubbles would you like to see? (Enter a number or press ENTER to keep current value): ")
            if top_k_input.strip().isdigit():
                top_k = int(top_k_input)
            else:
                bubbly_print("Keeping the current number of results ({}).".format(top_k), "ℹ️")

        elif profile_choice == "4":
            # Perform the query with the current filters
            bubbly_print(f"Performing query with text: '{query_text or 'None'}', category: '{query_category or 'None'}', showing top {top_k} results.", "🚀")
            profile = handle_action(client, action="query_user_profile", user_name=user_name, query_text=query_text, query_category=query_category, top_k=top_k)
            display_profile(profile)

        elif profile_choice == "5":
            # Exit profile mode
            bubbly_print(f"Exiting profile mode for user: {user_name} 🚪", "👋")
            break

        else:
            bubbly_print("Invalid choice! Please try again. 💫", "🤔")

def display_profile(profile):
    """
    Helper function to display the user profile.
    """
    if 'message' in profile:
        bubbly_print(profile['message'], "😕")
    else:
        bubbly_print(f"Profile of {profile['user']} 🧑‍💻")
        print(f"Total bubbles: {profile['total_bubbles']}")
        print("Recent bubbles:")
        for bubble in profile['bubbles']:
            print(f"💬 {bubble['content']} (Category: {bubble['category']})")

if __name__ == "__main__":
    bubbly_print("🌟 Welcome to Bubbl.ai! 🌟", "✨")
    bubbly_print("You're about to dive into the world of bubbles – your thoughts, ideas, and musings all wrapped up in one fun, floating place!", "💭")

    user = None
    with open("users.json", "r") as f:
        users = json.load(f)
    print("\n👋 Let's get started! Please sign up or log in to Bubbl.ai.",
          "\n1. 📝 Register",
          "\n2. 🔑 Log in",
          "\n3. 🚨 Deregister",
          "\n4. 🚪 Exit",
          "\n" + "-"*40 + "\n")
    while True:
        choice = input("👉 Make your bubbly choice (1-4): ")
        if choice == "1":
            # Register
            user_name = input("Enter your bubbly username: ")
            password = input("Enter your bubbly password: ")
            result = handle_action(None, action="register_user", users=users, user=user_name, password=password)
            if result and 'users' in result:
                bubbly_print("🎉 Registration successful! You're now a Bubblr! 🎉", "🎈")
                user = user_name
                users = result.get('users')
                with open("users.json", "w") as f:
                    json.dump(users, f, indent=4)
                if input("Do you want to continue with login / registration? (yes/no): ") == "yes":
                    continue
                break
            else:
                bubbly_print("Oops! Something went wrong during registration. Try again?", "😬")
        elif choice == "2":
            # Log in
            user_name = input("Enter your bubbly username: ")
            password = input("Enter your bubbly password: ")
            result = handle_action(None, action="login_user", users=users, user=user_name, password=password)
            if result:
                bubbly_print("🎉 Login successful! Welcome back to Bubbl.ai! 🎉", "🎈")
                user = user_name
                break
            else:
                bubbly_print("Oops! Something went wrong during login. Try again?", "😬")
        elif choice == "3":
            # Deregister
            result = handle_action(None, action="deregister_user", users=users, user=user)
            if result and 'users' in result:
                bubbly_print("🎉 Deregistration successful! You're no longer a Bubblr. Come back soon! 🎉", "🎈")
                users = result.get('users')
                with open("users.json", "w") as f:
                    json.dump(users, f, indent=4)
                if input ("Do you want to continue with login / registration? (yes/no): ") == "yes":
                    continue
                break
            else:
                bubbly_print("Oops! Something went wrong during deregistration. Try again?", "😬")
        elif choice == "4":
            # Exit the CLI
            bubbly_print("Thank you for visiting Bubbl.ai! Until next time, keep your thoughts floating! ✨", "👋")
            exit(0)
        else:   
            bubbly_print("Oops! That wasn't a valid choice. Let's try again! 💫", "🤔")

    print_menu()
   
    client = connect_weaviate_client()
    if not client:
        bubbly_print("Oops! We couldn't connect to the server. Please try again later.", "😕")
        exit(1)
    try:
        handle_action(client, action="create_bubble_schema")

        while True:
            choice = input("👉 Make your bubbly choice (1-8): ")
            
            if not choice.isdigit() or not 1 <= int(choice) <= 8:
                bubbly_print("Oops! That wasn't a valid choice. Let's try again! 💫", "🤔")
                continue

            if choice == "1":
                # Insert a bubble
                bubbly_print("Let's blow a new bubble! 🎈")
                content = input("What's on your mind? Tell me and I'll bubble it up: ")
                category = input("How would you categorize this bubble, e.g., Technology, Life, Fun. (Press ENTER to skip): ")
                bubble = [{"content": content, "user": user, "category": category}]
                result = handle_action(client, action="insert_bubbles", bubbles=bubble)
                if result:
                    bubbly_print(f"Bubbles inserted with IDs: {result}")
                    bubbly_print("✨ Your thoughts are now safely floating as a bubble! ✨", "🫧")
                else:
                    bubbly_print("Oops, something went wrong while blowing your bubble. Try again?", "😬")

            elif choice == "2":
                # Search for bubbles by similarity
                bubbly_print("Ready to explore the bubbly world? Let's find some relevant bubbles! 🔍")
                query_text = input("Enter your search query: ")
                top_k = int(input("How many bubbles would you like to see? (Enter a number): "))
                bubbles = handle_action(client, action="search_bubbles", query_text=query_text, top_k=top_k)
                if bubbles:
                    print("🫧 Relevant Bubbles:")
                    for bubble in bubbles:
                        print(f"💬 {bubble['content']} (User: {bubble['user']}, Category: {bubble['category']})")
                else:
                    bubbly_print("No bubbles found. Try again with a different query! 🌈")

            elif choice == "3":
                # Search users by similarity
                bubbly_print("Let's find other Bubblers who think like you! 🫂")
                query_text = input("Enter your search query: ")
                top_k = int(input("How many bubbles would you like to use for others' summaries? (Enter a number): "))
                top_k_user = int(input("How many bubbles would you like to use for your own summary? (Enter a number): "))
                users = handle_action(client, action="search_users_by_query", query_text=query_text, top_k=top_k, top_k_user=top_k_user, user=user)
                if users:
                    print("🎈 Bubblers with similar thoughts:")
                    for user in users:
                        print(f"👤 User: {user['user']}, Similarity: {user['similarity'] * 100:.2f}%")
                else:
                    bubbly_print("No like-minded Bubblers found. Try something else! 🌟")

            elif choice == "4":
                # Remove a bubble
                bubbly_print("Time to pop a bubble! 🗑️")
                uuid = input("Enter the UUID of the bubble you'd like to pop: ")
                success = handle_action(client, action="remove_bubble", uuid=uuid)
                if success:
                    bubbly_print(f"✨ Bubble with UUID {uuid} has been successfully popped! ✨", "🎉")
                else:
                    bubbly_print(f"Oops! Could not pop the bubble with UUID {uuid}. Maybe it floated away? 🧐")

            elif choice == "5":
                # Enter User Profile Mode
                bubbly_print("Let's check out a Bubblr's profile! 👤")
                user_name = input("Enter the username of the Bubblr you'd like to explore: ")
                user_profile_mode(client, user_name)

            elif choice == "6":
                # Insert bubbles from a JSON file
                bubbly_print("Time to blow some bubbles from a JSON file! 🎈")
                json_file = input("Enter the path to your bubbly JSON file: ")
                try:
                    with open(json_file, "r") as f:
                        json_data = json.load(f)
                    result = handle_action(client, action="insert_bubbles_from_json", json_data=json_data)
                    if result:
                        bubbly_print(f"Bubbles inserted with IDs: {result}")
                        bubbly_print("🎉 Bubbles from the JSON file are now floating in Bubbl.ai! 🎉")
                    else:
                        bubbly_print("Uh-oh! Something went wrong while inserting bubbles from JSON.", "😬")
                except FileNotFoundError:
                    bubbly_print("Oops! The file was not found. Double-check your path! 🚫")

            elif choice == "7":
                # Remove all bubbles with confirmation
                bubbly_print("⚠️ Are you sure you want to pop ALL the bubbles? This action is irreversible! ⚠️")
                confirmation = input("Type 'yes' if you're absolutely sure: ")
                if confirmation.lower() == 'yes':
                    success = handle_action(client, action="remove_all_bubbles", confirmation=confirmation)
                    if success:
                        bubbly_print("💨 Poof! All bubbles have been popped, and the slate is clean! 🫧")
                    else:
                        bubbly_print("Something went wrong, and the bubbles are still here. Try again? 🌈")
                else:
                    bubbly_print("Whew! That was close. The bubbles are safe. 😊", "😌")

            elif choice == "8":
                # Exit the CLI
                bubbly_print("Thank you for visiting Bubbl.ai! Until next time, keep your thoughts floating! ✨", "👋")
                break

            print_menu()
    finally:
        client.close()