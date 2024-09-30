import json
from src import connect_weaviate_client, handle_action

def bubbly_print(message, emoji="💬"):
    print(f"{emoji} {message}")

def print_menu():
    print("\n🎈 What bubbly adventure would you like to embark on today?")
    print("1. 💭 Blow a new Bubble (Insert a Bubble)")
    print("2. 🔍 Explore Bubbles (Search Bubbles)")
    print("3. 🔍 Find Like-minded Bubblers (Search Users by Similarity)")
    print("4. 🗑️  Pop a Bubble (Remove a Bubble)")
    print("5. 📂 Blow Bubbles from JSON (Insert Bubbles from a JSON file)")
    print("6. 🚨 Pop ALL the Bubbles (Remove All Bubbles with Confirmation)")
    print("7. 🚪 Exit Bubbl.ai")
    print("\n" + "-"*40 + "\n")

if __name__ == "__main__":
    bubbly_print("🌟 Welcome to Bubbl.ai! 🌟", "✨")
    bubbly_print("You're about to dive into the world of bubbles – your thoughts, ideas, and musings all wrapped up in one fun, floating place!", "💭")
    print_menu()
   
    client = connect_weaviate_client()
    if not client:
        bubbly_print("Oops! We couldn't connect to the server. Please try again later.", "😕")
        exit(1)
    try:
        handle_action(client, action="create_bubble_schema")

        while True:
            choice = input("👉 Make your bubbly choice (1-7): ")
            
            if not choice.isdigit() or not 1 <= int(choice) <= 7:
                bubbly_print("Oops! That wasn't a valid choice. Let's try again! 💫", "🤔")
                continue

            if choice == "1":
                # Insert a bubble
                bubbly_print("Let's blow a new bubble! 🎈")
                user = input("Enter your bubbly username: ")
                content = input("What's on your mind? Tell me and I'll bubble it up: ")
                category = input("How would you categorize this bubble (e.g., Technology, Life, Fun). Press ENTER to skip: ")
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
                top_k = int(input("How many bubbles would you like to see? (Enter a number): "))
                users = handle_action(client, action="search_users", query_text=query_text, top_k=top_k)
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

            elif choice == "6":
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

            elif choice == "7":
                # Exit the CLI
                bubbly_print("Thank you for visiting Bubbl.ai! Until next time, keep your thoughts floating! ✨", "👋")
                break

            print_menu()
    finally:
        client.close()