import os
import logging

import numpy as np
import openai
import weaviate
import weaviate.classes as wvc
from sklearn.metrics.pairwise import cosine_similarity
from typing import List, Dict

# Configure logging
logging.basicConfig(level=logging.INFO, filename="messages.log")

# Environment variables for configuration
WCS_URL = os.getenv("WCS_URL")
WCS_API_KEY = os.getenv("WCS_API_KEY")
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
        cluster_url=WCS_URL,
        auth_credentials=weaviate.auth.AuthApiKey(WCS_API_KEY),
        headers={
            "X-OpenAI-Api-Key": OPENAI_API_KEY
        }
    )

def query_most_relevant_bubbles(client, user: str, query_text: str, k: int = 10):
    """
    Query the 'Bubble' collection to find the most relevant k bubbles based on a text query.
    """
    logging.info("Querying top %d most relevant bubbles for text: '%s'...", k, query_text)
    bubble_collection = client.collections.get("Bubble")
    
    response = bubble_collection.query.near_text(
        query_text,
        limit=k,
        filters=wvc.query.Filter.by_property("user").not_equal(f"{user}")  # Exclude current user's bubbles
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

def query_user_profile(client, user_name: str, query_text: str = "", query_category: str = "", top_k: int = 10):
    """
    Query a user's profile based on their username.
    Returns the latest bubbles created by the user and other metadata.
    """
    logging.info("Starting query for user: '%s', category: '%s', and query text: '%s'.", user_name, query_category, query_text)
    logging.info("Fetching up to %d recent bubbles.", top_k)

    # Query the 'Bubble' collection for bubbles by this user
    bubble_collection = client.collections.get("Bubble")
    
    # Constructing the filter for the user and optionally the category
    logging.info("Building filters for user and category.")
    filters = wvc.query.Filter.by_property("user").like(f"{user_name}*")
    if query_category:
        logging.info("Adding category filter for: '%s'.", query_category)
        filters &= wvc.query.Filter.by_property("category").like(f"{query_category}*")

    # Perform the query based on whether query_text is provided
    if query_text:
        logging.info("Performing near_text search with query text: '%s'.", query_text)
        try:
            response = bubble_collection.query.near_text(
                query=query_text,
                filters=filters,
                limit=top_k,
            )
        except Exception as e:
            logging.error("An error occurred during near_text query execution: %s", e)
            return None
    else:
        logging.info("Performing fetch_objects query without near_text.")
        try:
            response = bubble_collection.query.fetch_objects(
                filters=filters,
                limit=top_k,
            )
        except Exception as e:
            logging.error("An error occurred during fetch_objects query execution: %s", e)
            return None
    
    # Process the response and extract user-specific data
    logging.info("Processing query response.")
    user_bubbles = []
    if response.objects:
        for obj in response.objects:
            bubble_data = {
                "content": obj.properties.get('content'),
                "category": obj.properties.get('category'),
                "created_at": obj.properties.get('created_at')  # Assuming 'created_at' is a property
            }
            logging.info("Bubble found: %s... (Category: %s)", bubble_data['content'][:50], bubble_data['category'])
            user_bubbles.append(bubble_data)
        logging.info("Query complete. Found %d bubbles for user: '%s'.", len(user_bubbles), user_name)
    else:
        logging.info("No bubbles found for user: '%s'.", user_name)
    
    # Additional user profile metadata
    profile_data = {
        "user": user_name,
        "total_bubbles": len(user_bubbles),  # Total number of bubbles
        "bubbles": user_bubbles
    }
    
    
    return profile_data

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
    Embed a text using OpenAI's embedding API.
    """
    logging.info("Embedding text with OpenAI: %s...", text[:50])  # Log first 50 chars for context
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

def insert_bubbles(client, bubbles: List[Dict]):
    """
    Insert bubbles into the Weaviate database.
    """
    logging.info("Inserting bubbles into the database...")
    
    objects = []
    for bubble in bubbles:
        obj = {
            "class": "Bubble",
            "properties": bubble
        }
        objects.append(obj)

    try:
        response = client.collections.get("Bubble").data.insert_many(
            [wvc.data.DataObject(properties=bubble) for bubble in bubbles]
        )
        return response.uuids
    except Exception as e:
        logging.error("An error occurred: %s", e)
    return None

def remove_bubble(client, user: str, uuid: str):
    """
    Remove a bubble from the Weaviate database by UUID.
    """
    logging.info("Removing bubble with UUID %s...", uuid)
    old_bubble = client.collections.get("Bubble").query.fetch_object_by_id(uuid)
    if old_bubble and old_bubble.properties.get("user") != user:
        logging.error("User %s does not have permission to delete bubble with UUID %s.", user, uuid)
        return False
    try:
        # Deleting the object using the UUID
        client.collections.get("Bubble").data.delete_by_id(uuid)
        logging.info("Bubble with UUID %s removed successfully.", uuid)
        return True
    except Exception as e:
        logging.error("An unexpected error occurred: %s", e)

def perform_similarity_search_bubbles(client, user: str, query_text: str, top_k: int):
    """
    Perform a similarity search for the most relevant bubbles based on a query.
    """
    bubbles = query_most_relevant_bubbles(client, user, query_text, top_k)
    return bubbles

def perform_similarity_search_users(client, user: str, query_text: str, top_k: int):
    """
    Perform a similarity search for the most relevant users based on their summaries.
    """
    bubbles = query_most_relevant_bubbles(client, user, query_text, top_k)
    bubbles_by_user = group_bubbles_by_user(bubbles)
    summary_by_user = summarize_user_content(bubbles_by_user)
    query_embedding = embed_text_with_openai(query_text)
    embedding_by_user = embed_user_summaries(summary_by_user)
    ranked_users = compute_user_similarity(embedding_by_user, query_embedding)
    return ranked_users

def perform_similarity_search_users_by_profile(client, user: str, query_text: str, top_k: int, top_k_user: int):
    """
    Perform a similarity search for the most relevant users based on their profiles and the current user's profile.
    """
    user_profile = query_user_profile(client, user, query_text, top_k_user)
    if user_profile['total_bubbles'] == 0:
        return []
    user_summary = summarize_user_content({user: user_profile['bubbles']})
    bubbles = query_most_relevant_bubbles(client, user, query_text, top_k)
    bubbles_by_user = group_bubbles_by_user(bubbles)
    summary_by_user = summarize_user_content(bubbles_by_user)
    summary_embedding = embed_text_with_openai(user_summary[user])
    embedding_by_user = embed_user_summaries(summary_by_user)
    ranked_users = compute_user_similarity(embedding_by_user, summary_embedding)
    return ranked_users

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
        logging.info("Bubble collection created")
        logging.debug("Config check: %s", bubbles.config.get(simple=True) is not None)
        return True
    else:
        logging.info("Bubble collection already exists.")
    return False

def remove_all_bubbles(client):
    """
    Delete the entire 'Bubble' class schema (removes all bubbles) and re-create it.
    """
    
    try:
        logging.info("🧼 Popping all the bubbles by deleting the 'Bubble' class schema...")

        # Delete the 'Bubble' class schema
        if client.collections.get('Bubble'):
            client.collections.delete('Bubble')
            logging.info("💨 'Bubble' class has been deleted!")

            # Re-create the 'Bubble' schema
            create_bubble_schema(client)
            logging.info("✨ 'Bubble' class has been re-created! You're ready to bubble again! 🫧")
        
        else:
            logging.info("❌ 'Bubble' class does not exist!")
        
        return True

    except Exception as e:
        logging.error("An error occurred while deleting and re-creating the schema: %s", e)
    return False

def insert_bubbles_from_json(client, json_data: List[Dict]):
    """
    Insert bubbles into the Weaviate database from a provided JSON data.
    """
    try:
        # Insert bubbles in bulk using insert_many
        response = client.collections.get("Bubble").data.insert_many(
            [wvc.data.DataObject(properties=bubble) for bubble in json_data]
        )

        # Retrieve and print all generated UUIDs
        if response.uuids:
            return response.uuids
    except Exception as e:
        logging.error("An error occurred: %s", e)
    return None

# Main function, now I/O-free
def handle_action(client, user, action, **kwargs):
    """
    The handle_action function orchestrates actions based on the provided action argument.
    It expects a Weaviate client, the action type, and additional parameters passed through kwargs.
    """

    if action == "insert_bubbles":
        # Insert bubbles using user-provided content and category
        bubbles = kwargs.get('bubble_data')
        return insert_bubbles(client, bubbles)

    elif action == "remove_bubble":
        # Remove a bubble using a UUID
        uuid = kwargs.get('uuid')
        return remove_bubble(client, user, uuid)

    elif action == "search_bubbles":
        # Search for the most relevant bubbles based on a query
        query_text = kwargs.get('query_text')
        top_k = kwargs.get('top_k', 5)
        return perform_similarity_search_bubbles(client, user, query_text, top_k)

    elif action == "search_users_by_profile":
        # Search for the most relevant users based on their summaries and the current user's profile
        query_text = kwargs.get('query_text')
        top_k = kwargs.get('top_k', 5)
        top_k_user = kwargs.get('top_k_user', 5)
        return perform_similarity_search_users_by_profile(client, user, query_text, top_k, top_k_user)
        
    elif action == "search_users_by_query":
        # Search for the most relevant users based on similarity of their bubbles
        query_text = kwargs.get('query_text')
        top_k = kwargs.get('top_k', 5)
        return perform_similarity_search_users(client, user, query_text, top_k)

    elif action == "query_user_profile":
        user_name = kwargs.get('user_name', user)
        query_text = kwargs.get('query_text', "")
        query_category = kwargs.get('query_category', "")
        top_k = kwargs.get('top_k', 5)
        return query_user_profile(client, user_name, query_text, query_category, top_k)

    elif action == "remove_all_bubbles":
        # Remove all bubbles with confirmation
        confirmation = kwargs.get('confirmation', 'no')
        if confirmation.lower() == "yes":
            return remove_all_bubbles(client)
        else:
            return False

    elif action == "insert_bubbles_from_json":
        # Insert bubbles from provided JSON data
        json_data = kwargs.get('json_data')
        return insert_bubbles_from_json(client, json_data)

    elif action == "create_bubble_schema":
        # Create the bubble schema if it doesn't already exist
        return create_bubble_schema(client)
    
    elif action == "register_user":
        # Register a new user
        users = kwargs.get('users', {})
        password = kwargs.get('password')
        if user not in users:
            users[user] = password
            return {'users': users}
        return None
    
    elif action == "deregister_user":
        # Deregister a user
        users = kwargs.get('users', {})
        if user_name in users:
            del users[user]
            return {'users': users}
        return None
    
    elif action == "login_user":
        # Login a user
        users = kwargs.get('users', {})
        password = kwargs.get('password')
        if user in users and password == users[user]:
            return True
        return False

    else:
        raise ValueError("Invalid action specified.")