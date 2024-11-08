"""
BSD 3-Clause License

Copyright (c) 2024, yamaceay

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright notice, this
    list of conditions and the following disclaimer.

2. Redistributions in binary form must reproduce the above copyright notice,
    this list of conditions and the following disclaimer in the documentation
    and/or other materials provided with the distribution.

3. Neither the name of the copyright holder nor the names of its
    contributors may be used to endorse or promote products derived from
    this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

Author: Yamaç Eren Ay
"""

import datetime
import logging

from typing import List, Dict, Optional, Union
import numpy as np
import asyncio
import openai
import weaviate
import weaviate.classes as wvc
import humanize

# Configure logging
logging.basicConfig(level=logging.INFO, filename="messages.log")

class BubbleError(Exception):
    """Base class for all bubble-related exceptions."""
    pass


class DuplicateBubbleError(BubbleError):
    """Raised when trying to insert a duplicate bubble."""
    def __init__(self, message="Bubble already exists with the same content."):
        self.message = message
        super().__init__(self.message)


class BubbleNotFoundError(BubbleError):
    """Raised when trying to remove or query a non-existent bubble."""
    def __init__(self, message="Bubble not found."):
        self.message = message
        super().__init__(self.message)


class InvalidUserError(BubbleError):
    """Raised when a user attempts an unauthorized action."""
    def __init__(self, message="Unauthorized action by the user."):
        self.message = message
        super().__init__(self.message)


class DatabaseError(BubbleError):
    """Raised when a database operation fails."""
    def __init__(self, message="A database error occurred. Please try again later."):
        self.message = message
        super().__init__(self.message)


def connect_weaviate_client(openai_api_key: str, wcs_url: str, wcs_api_key: str):
    """
    Connect to the Weaviate instance with the required API key and URL.
    """
    return weaviate.connect_to_wcs(
        cluster_url=wcs_url,
        auth_credentials=weaviate.auth.AuthApiKey(wcs_api_key),
        headers={
            "X-OpenAI-Api-Key": openai_api_key
        }
    )

def perform_query(client, query_user: str = "", not_query_user: str = "", query_text: str = "", query_category: str = "", limit: int = 10, offset: int = 0):
    """
    Perform a query to find bubbles by a specific user and optionally a category.
    """
    # Query the 'Bubble' collection for bubbles by this user
    bubble_collection = client.collections.get("Bubble")
    
    # Constructing the filter for the user and optionally the category
    logging.info("Building filters for user and category.")
    filters = wvc.query.Filter.by_property("content").like("*")  # Default filter to match all content (wildcard)
    if query_user and not_query_user and query_user == not_query_user:
        logging.error("Both query_user and not_query_user cannot be provided simultaneously.")
        return None
    if query_user:
        logging.info("Adding user filter for: '%s'.", query_user)
        filters &= wvc.query.Filter.by_property("user").equal(query_user)
    elif not_query_user:
        logging.info("Adding not user filter for: '%s'.", not_query_user)
        filters &= wvc.query.Filter.by_property("user").not_equal(not_query_user)
    if query_category:
        logging.info("Adding category filter for: '%s'.", query_category)
        filters &= wvc.query.Filter.by_property("category").equal(query_category)

    # Perform the query based on whether query_text is provided
    if query_text:
        logging.info("Performing near_text search with query text: '%s'.", query_text)
        try:
            response = bubble_collection.query.near_text(
                query=query_text,
                filters=filters,
                limit=limit,
                offset=offset,
                return_metadata=wvc.query.MetadataQuery(creation_time=True),
            )
        except Exception as e:
            logging.error("An error occurred during near_text query execution: %s", e)
            return None
    else:
        logging.info("Performing fetch_objects query without near_text.")
        try:
            response = bubble_collection.query.fetch_objects(
                filters=filters,
                limit=limit,
                offset=offset,
                return_metadata=wvc.query.MetadataQuery(creation_time=True),
                sort=wvc.query.Sort.by_property(name="_creationTimeUnix", ascending=False),  # Use timestamp index for sorting
            )
        except Exception as e:
            logging.error("An error occurred during fetch_objects query execution: %s", e)
            return None
    
    return response

def process_bubbles_response(response):
    bubbles = []
    if not response or not hasattr(response, 'objects'):
        return bubbles

    for obj in response.objects:
        bubble_data = {
            "content": obj.properties.get('content'),
            "user": obj.properties.get('user'),
            "category": obj.properties.get('category'),
            "created_at": obj.metadata.creation_time,
            "uuid": obj.uuid
        }
        bubbles.append(bubble_data)
    return bubbles

def query_most_relevant_bubbles(client, not_query_user: str = "", query_user: str = "", query_text: str = "", query_category: str = "", limit: int = 10, offset: int = 0):
    """
    Query the 'Bubble' collection to find the most relevant k bubbles based on a text query.
    """
    logging.info("Querying top %d most relevant bubbles for text: '%s'...", limit, query_text)
    
    # Perform the query
    response = perform_query(client, query_user=query_user, not_query_user=not_query_user, query_text=query_text, query_category=query_category, limit=limit, offset=offset)
    bubbles = process_bubbles_response(response)
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

async def summarize_with_gpt(content: str) -> str:
    """
    Asynchronously call OpenAI's chat-based API to summarize the given content using the correct endpoint for chat models.
    """
    logging.info("Summarizing content with GPT: %s...", content[:50])

    # Define the message structure for GPT-4 chat model
    messages = [
        {"role": "system", "content": "You are a helpful assistant that summarizes content."},
        {"role": "user", "content": f"Summarize the following content:\n\n{content}"}
    ]

    # Call the GPT-4 or GPT-3.5-turbo chat model to summarize the content
    response = await asyncio.to_thread(
        openai.chat.completions.create,
        model="gpt-4o",
        messages=messages,
        temperature=0.7,
        max_tokens=100
    )

    # Extract the summarized content from the response
    summary = response.choices[0].message.content.strip()
    return summary

async def summarize_user_content_async(user_bubbles: Dict[str, str]) -> Dict[str, str]:
    """
    Summarize the content for each user using GPT in an asynchronous and efficient manner.
    """
    logging.info("Summarizing user content with GPT...")

    # Prepare async tasks to summarize content for each user
    tasks = [summarize_with_gpt(content) for content in user_bubbles.values()]

    # Gather all summaries in parallel
    summaries = await asyncio.gather(*tasks)

    # Return a dictionary mapping users to their summaries
    return {user: summary for user, summary in zip(user_bubbles.keys(), summaries)}

async def embed_text_with_openai_async(text: str) -> np.ndarray:
    """
    Embed a text asynchronously using OpenAI's embedding API in a thread.
    """
    logging.info("Embedding text asynchronously with OpenAI: %s...", text[:50])
    
    # Run the synchronous OpenAI API call in a separate thread
    response = await asyncio.to_thread(openai.embeddings.create, input=text, model="text-embedding-ada-002")
    
    # Extract the embedding
    embedding = response.data[0].embedding
    return np.array(embedding)

async def embed_user_summaries_async(user_summaries: Dict[str, str]) -> Dict[str, np.ndarray]:
    """
    Embed each user's summary using OpenAI API asynchronously to create vector representations of user opinions.
    """
    tasks = [embed_text_with_openai_async(summary) for user, summary in user_summaries.items()]
    results = await asyncio.gather(*tasks)
    return {user: embedding for user, embedding in zip(user_summaries.keys(), results)}

def cosine_similarity(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    """
    Compute the cosine similarity between two vectors.
    """
    return np.dot(a, b.T) / (np.linalg.norm(a) * np.linalg.norm(b))

def compute_user_similarity(user_embeddings: Dict[str, np.ndarray], query_embedding: np.ndarray) -> List[Dict[str, float]]:
    """
    Compute cosine similarity between each user's embedding and the query embedding.
    Return a list of users ranked by their similarity score.
    """
    logging.info("Computing cosine similarity between users and the query...")
    
    similarities = []
    
    for user, embedding in user_embeddings.items():
        similarity = cosine_similarity(embedding, query_embedding)
        similarities.append({"user": user, "similarity": similarity})
    
    # Sort users by similarity in descending order
    similarities = sorted(similarities, key=lambda x: x["similarity"], reverse=True)
    
    return similarities

def insert_bubbles(client, bubbles: List[Dict]):
    """
    Insert bubbles into the Weaviate database.
    Raises DuplicateBubbleError if a bubble with the same content exists.
    """
    logging.info("Inserting bubbles into the database...")
    
    collection = client.collections.get("Bubble")

    for bubble in bubbles:
        user_filter = wvc.query.Filter.by_property("user").equal(bubble["user"])
        content_filter = wvc.query.Filter.by_property("content").equal(bubble["content"])
        result = collection.query.fetch_objects(
            filters=user_filter & content_filter,
        )
        if result.objects:
            raise DuplicateBubbleError(f"Bubble with content '{bubble['content']}' already exists.")
    try:
        objects = [wvc.data.DataObject(properties=bubble) for bubble in bubbles]
        response = collection.data.insert_many(objects)
        return response.uuids
    except Exception as e:
        logging.error("An error occurred: %s", e)
        raise DatabaseError("Failed to insert bubbles into the database.")

def get_bubble(client, user: str, uuid: str) -> tuple[Optional[Dict], bool]:
    """
    Check if a bubble is removable by the user.
    """
    logging.info("Checking if bubble with UUID %s is removable...", uuid)
    old_bubble = client.collections.get("Bubble").query.fetch_object_by_id(uuid)
    return old_bubble, old_bubble.properties.get("user") == user

def remove_bubble(client, user: str, uuid: str):
    """
    Remove a bubble from the Weaviate database by UUID.
    Raises BubbleNotFoundError if the bubble is not found or does not belong to the user.
    """
    old_bubble, permission = get_bubble(client, user, uuid)
    if not old_bubble:
        raise BubbleNotFoundError(f"No bubble found with UUID {uuid}.")
    if not permission:
        raise InvalidUserError("You do not have permission to delete this bubble.")
    try:
        client.collections.get("Bubble").data.delete_by_id(uuid)
        logging.info("Bubble with UUID %s removed successfully.", uuid)
        return True
    except Exception as e:
        logging.error("An unexpected error occurred: %s", e)
        raise DatabaseError("Failed to remove the bubble.")

async def perform_similarity_search_users_by_profile(
        client, 
        user: str, 
        query_text: str, 
        query_category: str, 
        limit: int, 
        limit_user: int,
    ):
    """
    Perform a similarity search for the most relevant users based on their profiles and the current user's profile.
    """
    bubbles_user = query_most_relevant_bubbles(client, query_user=user, query_text=query_text, query_category=query_category, limit=limit_user)
    if len(bubbles_user) == 0:
        raise BubbleNotFoundError("No user profile found for the current user.")
    bubbles = query_most_relevant_bubbles(client, not_query_user=user, query_text=query_text, query_category=query_category, limit=limit)
    if len(bubbles) == 0:
        raise BubbleNotFoundError("No user profiles found for the query.")
    bubbles.extend(bubbles_user)
    bubbles_by_user = group_bubbles_by_user(bubbles)
    summary_by_user = await summarize_user_content_async(bubbles_by_user)
    embedding_by_user = await embed_user_summaries_async(summary_by_user)
    embedding_user = embedding_by_user.pop(user)
    ranked_users = compute_user_similarity(embedding_by_user, embedding_user)
    return ranked_users

def create_bubble_schema(client):
    """
    Create a 'Bubble' collection if it doesn't exist, with indexing by vector and timestamp.
    """
    if not client.collections.exists("Bubble"):
        bubbles = client.collections.create(
            name="Bubble",
            vectorizer_config=wvc.config.Configure.Vectorizer.text2vec_openai(),    # Use OpenAI API for text2vec
            generative_config=wvc.config.Configure.Generative.cohere(),             # Use Cohere for generative tasks
            properties=[
                wvc.config.Property(name="content", data_type=wvc.config.DataType.TEXT),
                wvc.config.Property(name="user", data_type=wvc.config.DataType.TEXT),
                wvc.config.Property(name="category", data_type=wvc.config.DataType.TEXT),
            ]
        )
        logging.info("Bubble collection created with vector indexing")
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
        collection = client.collections.get("Bubble")
        # Insert bubbles in bulk using insert_many
        with collection.batch.dynamic() as batch:
            for bubble in json_data:
                batch.add_object(properties=bubble)

        # Retrieve and print all generated UUIDs
        return True
    except Exception as e:
        logging.error("An error occurred: %s", e)
    return None

def bubble_add_time(bubbles: List[Dict]) -> List[Dict]:
    # Add created_at_str attribute for human-readable timestamps
    current_time = datetime.datetime.now(datetime.timezone.utc)
    for bubble in bubbles:
        created_at = bubble.get('created_at')
        if created_at:
            bubble['created_at_str'] = humanize.naturaltime(current_time - created_at)
        else:
            bubble['created_at_str'] = "Unknown time"
    return bubbles

class Handler:
    """
    Handler class to interact with the Weaviate client and perform various operations.
    """
    def __init__(self, client, user: str):
        self.client = client
        self.user = user

    def insert_bubbles(self, bubbles: List[Dict[str, Union[str, int]]]) -> Optional[List[str]]:
        """
        Insert bubbles using user-provided content and category.
        """
        return insert_bubbles(self.client, bubbles)

    def remove_bubble(self, uuid: str) -> bool:
        """
        Remove a bubble using its UUID.
        """
        return remove_bubble(self.client, self.user, uuid)
    
    def query_most_relevant_bubbles(self, query_user: str = "", query_text: str = "", query_category: str = "", limit: int = 10, offset: int = 0) -> Optional[List[Dict[str, Union[str, int]]]]:
        """
        Query the most relevant bubbles based on the provided text and category.
        """
        bubbles = query_most_relevant_bubbles(self.client, query_user=query_user, query_text=query_text, query_category=query_category, limit=limit, offset=offset)
        return bubble_add_time(bubbles)

    async def search_users_by_profile(self, query_text: str = "", query_category: str = "", limit: int = 50, limit_user: int = 5) -> Optional[List[Dict[str, float]]]:
        """
        Search for the most relevant users based on the current user's profile.
        """
        return await perform_similarity_search_users_by_profile(self.client, self.user, query_text, query_category, limit, limit_user)


    def remove_all_bubbles(self, confirmation: str = 'no') -> bool:
        """
        Remove all bubbles with confirmation.
        """
        if confirmation.lower() == "yes":
            return remove_all_bubbles(self.client)
        return False

    def insert_bubbles_from_json(self, json_data: List[Dict[str, Union[str, int]]]) -> Optional[List[str]]:
        """
        Insert bubbles from provided JSON data.
        """
        return insert_bubbles_from_json(self.client, json_data)

    def create_bubble_schema(self) -> bool:
        """
        Create the bubble schema if it doesn't already exist.
        """
        return create_bubble_schema(self.client)