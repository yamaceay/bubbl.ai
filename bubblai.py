import os
import json
import weaviate.classes as wvc
import numpy as np
import weaviate
import openai
from typing import List, Dict
from sklearn.metrics.pairwise import cosine_similarity
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)

# Environment variables for configuration
URL = os.getenv("WCS_URL")
APIKEY = os.getenv("WCS_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Ensure OpenAI API key is properly loaded
if not OPENAI_API_KEY:
    raise ValueError("OpenAI API key is missing. Set it as an environment variable 'OPENAI_API_KEY'.")

# Initialize OpenAI API Key
openai.api_key = OPENAI_API_KEY

def connect_weaviate_client():
    """
    Connect to the Weaviate instance with the required API key and URL.
    """
    return weaviate.connect_to_wcs(
        cluster_url=URL,
        auth_credentials=weaviate.auth.AuthApiKey(APIKEY),
        headers={
            "X-OpenAI-Api-Key": OPENAI_API_KEY
        }
    )

def query_most_relevant_bubbles(client, query_text: str, k: int = 10):
    """
    Query the 'Bubble' collection to find the most relevant k bubbles based on a text query.
    """
    logging.info(f"Querying top {k} most relevant bubbles for text: '{query_text}'...")
    bubble_collection = client.collections.get("Bubble")
    
    response = bubble_collection.query.near_text(
        query_text,
        limit=k
    )
    
    # Process the response and extract properties
    bubbles = []
    for obj in response.objects:
        bubble_data = {
            "content": obj.properties.get('content'),
            "user": obj.properties.get('user'),
            "category": obj.properties.get('category')
        }
        bubbles.append(bubble_data)
    
    return bubbles

def group_bubbles_by_user(bubbles: List[Dict]):
    """
    Group the bubbles by user. Return a dictionary where the keys are users and values are concatenated content.
    """
    logging.info("Grouping bubbles by user...")
    user_bubbles = {}
    for bubble in bubbles:
        user = bubble['user']
        content = bubble['content']
        
        if user not in user_bubbles:
            user_bubbles[user] = content
        else:
            user_bubbles[user] += "\r\n" + content  # Concatenate the bubble content for each user.
    
    return user_bubbles

def summarize_user_content(user_bubbles: Dict[str, str]):
    """
    Summarize the content for each user. For simplicity, we're concatenating the content here.
    Advanced: You could use a GPT-based summarization model for more sophisticated summaries.
    """
    logging.info("Summarizing user content...")
    return {user: content for user, content in user_bubbles.items()}  # Simple concatenation for now


def embed_text_with_openai(text: str) -> np.ndarray:
    """
    Embed a text using OpenAI's new embedding API (openai>=1.0.0).
    """
    logging.info(f"Embedding text with OpenAI: {text[:50]}...")  # Log first 50 chars for context
    response = openai.embeddings.create(input=text, model="text-embedding-ada-002")
    embedding = response.data[0].embedding
    return np.array(embedding)

def embed_user_summaries(user_summaries: Dict[str, str]) -> Dict[str, np.ndarray]:
    """
    Embed each user's summary using OpenAI API to create vector representations of user opinions.
    """
    logging.info("Embedding user summaries...")
    user_embeddings = {}
    
    for user, summary in user_summaries.items():
        user_embeddings[user] = embed_text_with_openai(summary)
    
    return user_embeddings

def compute_user_similarity(user_embeddings: Dict[str, np.ndarray], query_embedding: np.ndarray) -> List[Dict[str, float]]:
    """
    Compute cosine similarity between each user's embedding and the query embedding.
    Return a list of users ranked by their similarity score.
    """
    logging.info("Computing cosine similarity between users and the query...")
    
    similarities = []
    
    for user, embedding in user_embeddings.items():
        similarity = cosine_similarity([embedding], [query_embedding])[0][0]
        similarities.append({"user": user, "similarity": similarity})
    
    # Sort users by similarity in descending order
    similarities = sorted(similarities, key=lambda x: x["similarity"], reverse=True)
    
    return similarities

def remove_bubble(client):
    """
    Remove a bubble from the Weaviate database by UUID.
    """
    uuid = input("Enter the UUID of the bubble to remove: ")
    
    try:
        # Deleting the object using the UUID
        client.collections.get("Bubble").data.delete_by_id(uuid)
        print(f"Bubble with UUID {uuid} removed successfully.")
    except weaviate.exceptions.UnexpectedStatusCodeException as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")

def perform_similarity_search_bubbles(client):
    """
    Perform a similarity search for the most relevant bubbles based on a query.
    """
    query_text = input("Enter your search query: ")
    top_k = int(input("Enter the number of bubble results to return: "))

    bubbles = query_most_relevant_bubbles(client, query_text, top_k)

    if bubbles:
        for i, bubble in enumerate(bubbles):
            print(f"{i+1}. Content: {bubble['content']}, User: {bubble['user']}, Category: {bubble['category']}")
    else:
        print("No relevant bubbles found.")

def perform_similarity_search_users(client):
    """
    Perform a similarity search for the most relevant users based on their summaries.
    """
    # Define a query to search for relevant bubbles
    query_text = input("Enter your search query: ")
    top_k = int(input("Enter the number of results to return: "))

    # Step 1: Fetch the most relevant k bubbles based on the query
    bubbles = query_most_relevant_bubbles(client, query_text, top_k)
    
    # Step 2: Group the bubbles by user
    user_bubbles = group_bubbles_by_user(bubbles)
    
    # Step 3: Summarize the content for each user
    user_summaries = summarize_user_content(user_bubbles)

    # Step 4: Embed the query text
    query_embedding = embed_text_with_openai(query_text)
    
    # Step 5: Embed user summaries
    user_embeddings = embed_user_summaries(user_summaries)

    # Step 6: Compute cosine similarity between the query and each user
    ranked_users = compute_user_similarity(user_embeddings, query_embedding)

    # Display ranked users based on their opinion alignment
    if ranked_users:
        print("Ranked Users by Opinion Alignment:")
        for i, user in enumerate(ranked_users):
            print(f"{i+1}. User: {user['user']}, Similarity: {user['similarity'] * 100:.2f}%")
    else:
        print("No relevant users found.")

def insert_bubbles(client):
    """
    Allow the user to insert multiple bubbles continuously and insert them at once using insert_many.
    """
    user = input("Enter your username: ")

    bubbles = []

    while True:
        print("\nWrite Mode: (Type your message below or type 'exit' to go back to the main menu)")

        content = input("Enter the content of the bubble (or 'exit' to finish): ")
        if content.lower() == 'exit':
            if not bubbles:
                print("No bubbles to insert. Returning to the main menu.")
            else:
                print("Inserting all bubbles...")

                # Use insert_many to insert all bubbles at once
                response = client.collections.get("Bubble").data.insert_many(
                    [wvc.data.DataObject(properties=bubble) for bubble in bubbles]
                )

                # Retrieve and print all generated UUIDs
                if response.uuids:
                    print(f"Bubbles inserted with UUIDs: {response.uuids}")
                else:
                    print("No bubbles were inserted.")

            break  # Exit the write mode

        category = input("Enter the category of the bubble: ")

        # Collect bubble data
        bubble = {
            "content": content,
            "user": user,
            "category": category
        }
        bubbles.append(bubble)  # Add bubble to the list

def insert_bubbles_from_json(client, json_file: str):
    """
    Insert bubbles into the Weaviate database from a JSON file.
    The JSON file should contain a list of bubbles with 'content', 'user', and 'category' fields.
    """
    try:
        # Load bubbles from JSON file
        with open(json_file, "r") as f:
            bubbles = json.load(f)

        if not bubbles:
            print("The JSON file is empty or not properly formatted.")
            return

        # Insert bubbles in bulk using insert_many
        print(f"Inserting bubbles from {json_file}...")
        response = client.collections.get("Bubble").data.insert_many(
            [wvc.data.DataObject(properties=bubble) for bubble in bubbles]
        )

        # Retrieve and print all generated UUIDs
        if response.uuids:
            print(f"Bubbles inserted with UUIDs: {response.uuids}")
        else:
            print("No bubbles were inserted.")
    except FileNotFoundError:
        print(f"Error: The file {json_file} was not found.")
    except json.JSONDecodeError:
        print("Error: The JSON file is not properly formatted.")
    except Exception as e:
        print(f"An error occurred: {e}")
def remove_all_bubbles(client):
    """
    Delete the entire 'Bubble' class schema (removes all bubbles) and re-create it.
    """
    confirmation = input("⚠️  Are you sure you want to delete **ALL** the bubbles by removing the schema? (yes/no): ").strip().lower()

    if confirmation == 'yes':
        try:
            print("🧼 Popping all the bubbles by deleting the 'Bubble' class schema...")

            # Delete the 'Bubble' class schema
            if client.collections.get('Bubble'):
                client.collections.delete('Bubble')
                print("💨 'Bubble' class schema deleted!")

                # Re-create the 'Bubble' schema
                create_bubble_schema(client)
                print("✨ 'Bubble' class schema has been re-created! You're ready to bubble again! 🫧")

            else:
                print("❌ 'Bubble' class schema does not exist!")

        except Exception as e:
            print(f"An error occurred while deleting and re-creating the schema: {e}")
    else:
        print("Whew! That was close. No bubbles were popped. 💭")


def create_bubble_schema(client):
    """
    Create a 'Bubble' collection if it doesn't exist.
    """
    if not client.collections.exists("Bubble"):
        bubbles = client.collections.create(
            name="Bubble",
            vectorizer_config=wvc.config.Configure.Vectorizer.text2vec_openai(),    # Use OpenAI API for text2vec
            generative_config=wvc.config.Configure.Generative.cohere(),             # Use Cohere for generative tasks
            properties=[
                wvc.config.Property(name="content", data_type=wvc.config.DataType.TEXT),
                wvc.config.Property(name="user", data_type=wvc.config.DataType.TEXT),
                wvc.config.Property(name="category", data_type=wvc.config.DataType.TEXT)
            ]
        )
        print("Bubble collection created:", bubbles.config.get(simple=True))
    else:
        print("Bubble collection already exists.")

def main():
    client = connect_weaviate_client()

    print("✨ Welcome to Bubbl.ai! ✨\n🌟 You are now a Bubbler! 🌟")
    if not client.collections.exists('Bubble'):

        # Re-create the 'Bubble' schema
        create_bubble_schema(client)
        print("💨 'Bubble' class schema created! You're ready to bubble! 🫧")

    try:
        while True:
            print("\n💬 What would you like to do?")
            print("1. 💭 Enter write mode (create multiple bubbles)")
            print("2. 🗑️  Remove a single bubble")
            print("3. 🔍 Search bubbles by similarity (based on text)")
            print("4. 🔍 Search users by similarity (based on their summaries)")
            print("5. 📂 Insert bubbles from a JSON file")
            print("6. 🚨 Remove all bubbles (⚠️ with confirmation!)")
            print("7. 🚪 Exit")

            choice = input("👉 Make your choice (1-7): ")

            if choice == "1":
                insert_bubbles(client)
            elif choice == "2":
                remove_bubble(client)
            elif choice == "3":
                perform_similarity_search_bubbles(client)
            elif choice == "4":
                perform_similarity_search_users(client)
            elif choice == "5":
                json_file = input("📄 Enter the JSON file path: ")
                insert_bubbles_from_json(client, json_file)
            elif choice == "6":
                remove_all_bubbles(client)
            elif choice == "7":
                print("✨ Thanks for bubbling with us! Until next time! ✨")
                break
            else:
                print("❌ Oops! That's not a valid option. Please try again!")

    finally:
        # Ensure the client connection is properly closed
        client.close()
        logging.info("Closed Weaviate client connection.")

if __name__ == "__main__":
    main()
