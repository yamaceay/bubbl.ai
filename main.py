from pydantic import BaseModel
from fastapi import FastAPI, HTTPException, Request
from fastapi.concurrency import asynccontextmanager
import weaviate
import os
import openai  # For summarization (optional, if not using Weaviate's built-in summarization)
from dotenv import load_dotenv
load_dotenv()

# Define a Pydantic model for the request body
class NoteRequest(BaseModel):
    user_id: str
    content: str
class_name = "Note"

app = FastAPI()

# Weaviate client setup (replace with your Weaviate instance URL and API key if needed)
client = weaviate.Client(
    url="http://localhost:8080"
)  # Or Weaviate Cloud URL

# Set OpenAI API key if using it for summarization (optional)
openai.api_key = os.getenv("OPENAI_API_KEY")

# Define the schema for the "Note" class
note_schema = {
    "classes": [
        {
            "class": class_name,
            "description": "A class to store user notes",
            "properties": [
                {
                    "name": "content",
                    "dataType": ["text"],
                    "description": "The content of the note"
                },
                {
                    "name": "user_id",
                    "dataType": ["string"],
                    "description": "The ID of the user who created the note"
                }
            ],
            "vectorizer": "text2vec-openai"  # Specifies that the OpenAI vectorizer is used
        }
    ]
}

# FastAPI app instance
@asynccontextmanager
async def lifespan(app: FastAPI):
    # During startup: Ensure schema exists
    try:
        schema = client.schema.get()  # Get the current schema from Weaviate
        classes = [class_["class"] for class_ in schema["classes"]]
        if class_name not in classes:
            client.schema.create(note_schema)  # Create the schema for the "Note" class
            print("Note schema created successfully!")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating schema: {str(e)}")
    
    yield

    # During shutdown: Any cleanup (if needed)
    # No cleanup needed for this application

# FastAPI app with lifespan event for startup and shutdown
app = FastAPI(lifespan=lifespan)

@app.get("/check-schema")
async def check_schema():
    try:
        schema = client.schema.get()  # Fetch current schema
        return schema  # Return the schema as JSON response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error checking schema: {str(e)}")

@app.post("/notes")
async def create_note(note: NoteRequest):
    """
    Create a new note for a user and store it in Weaviate. Weaviate handles the embedding.
    """
    try:
        # Extract user_id and content from the request body
        user_id = note.user_id
        content = note.content

        # Prepare note object for Weaviate (embeddings are automatically handled by Weaviate)
        note_object = {
            "class": class_name,
            "properties": {
                "content": content,
                "user_id": user_id
            }
        }

        # Store the note in Weaviate
        client.data_object.create(note_object, class_name)
        return {"status": "Note created successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/query")
async def query_notes(request: Request):
    """
    Query relevant notes from Weaviate based on a user's query and a limit on results.
    """
    try:
        # Extract the request body as JSON
        data = await request.json()

        # Extract `query` and `limit` from the request body
        query = data.get("query")  # Extracts the 'query' key
        limit = data.get("limit", 1000)  # Extracts the 'limit' key, defaults to 1000 if not provided

        # Ensure that the query is provided
        if not query:
            raise HTTPException(status_code=400, detail="Query parameter is required.")

        # Ensure that the query is a string or a list of strings (Weaviate expects a list of concepts)
        if isinstance(query, str):
            query = [query]  # Convert the string to a list with one element
        elif not isinstance(query, list) or not all(isinstance(q, str) for q in query):
            raise HTTPException(status_code=400, detail="Query must be a string or a list of strings.")

        # Weaviate's nearText query to retrieve relevant notes
            # .get("Note", ["content", "user_id"]) \
        # .with_near_text(query=query, limit=limit)\
        query_result = client.query\
            .get(class_name, ["content", "user_id"])\
            .with_limit(limit)\
            .do()

        # Process the query result and group notes by user
        notes_by_user = {}
        for result in query_result["data"]["Get"]["Note"]:
            user_id = result["user_id"]
            if user_id not in notes_by_user:
                notes_by_user[user_id] = []
            notes_by_user[user_id].append(result["content"])

        # Return grouped notes by user
        return {"grouped_notes": notes_by_user}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def summarize_user_opinions(notes):
    """
    Summarize a user's notes using OpenAI GPT (or any other summarization tool).
    """
    combined_notes = " ".join(notes)
    
    # Example: using OpenAI GPT to summarize the notes
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=f"Summarize these opinions: {combined_notes}",
        max_tokens=150
    )
    
    return response.choices[0].text.strip()
    
# at last, the bottom of the file/module
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)

# @app.get("/recommend/{user_id}")
# async def recommend_users(user_id: str):
#     """
#     Recommend users based on their similarity to the specified user.
#     """
#     try:
#         # Fetch all notes for the user to create a summary embedding
#         user_notes = (
#             client.query
#             .get(class_name, ["content"])
#             .with_where({
#                 "path": ["user_id"],
#                 "operator": "Equal",
#                 "valueString": user_id
#             })
#             .do()
#         )

#         if not user_notes["data"]["Get"][class_name]:
#             raise HTTPException(status_code=404, detail="User not found or no notes available")

#         # Combine all user's notes for summarization
#         user_content = " ".join([note["content"] for note in user_notes["data"]["Get"][class_name]])
#         user_summary = summarize_user_opinions([user_content])

#         # Generate embedding for user summary (Weaviate handles embedding generation)
#         user_embedding = client.query.get(class_name, ["_additional { vector }"]).with_near_text({
#             "concepts": [user_summary]
#         }).do()

#         # Perform a search for similar users based on the user's summary embedding
#         similar_users = (
#             client.query
#             .get(class_name, ["user_id"])
#             .with_near_vector({
#                 "vector": user_embedding["data"]["Get"][class_name][0]["_additional"]["vector"]
#             })
#             .with_limit(5)
#             .do()
#         )

#         recommended_user_ids = set([result["user_id"] for result in similar_users["data"]["Get"][class_name]])
#         return {"recommended_users": list(recommended_user_ids)}

#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))

# @app.post("/notes")
# async def create_note(user_id: str, content: str):
#     # Prepare note object for Weaviate (embeddings are automatically handled by Weaviate)
#     note_object = {
#         "class": class_name,
#         "properties": {
#             "content": content,
#             "user_id": user_id
#         }
#     }
#     client.data_object.create(note_object)
#     return {"status": "Note created successfully"}

# from fastapi import FastAPI, HTTPException, Request
# import weaviate

# app = FastAPI()

# # Weaviate client setup
# client = weaviate.Client("http://localhost:8080")

# @app.post("/query")
# async def query_notes(request: Request):
#     """
#     Query relevant notes from Weaviate based on a user's query and a limit on results.
#     """
#     try:
#         # Extract the request body as JSON
#         data = await request.json()

#         # Extract `query` and `limit` from the request body
#         query = data.get("query")  # Extracts the 'query' key
#         limit = data.get("limit", 1000)  # Extracts the 'limit' key, defaults to 1000 if not provided

#         # Ensure that the query is provided
#         if not query:
#             raise HTTPException(status_code=400, detail="Query parameter is required.")

#         # Weaviate's nearText query to retrieve relevant notes
#         query_result = (
#             client.query
#             .get(class_name, ["content", "user_id"])
#             .with_near_text({"concepts": [query]})
#             .with_limit(limit)
#             .do()
#         )

#         # Group notes by user for summarization
#         notes_by_user = {}
#         for result in query_result["data"]["Get"][class_name]:
#             user_id = result["user_id"]
#             if user_id not in notes_by_user:
#                 notes_by_user[user_id] = []
#             notes_by_user[user_id].append(result["content"])

#         # Summarize each user's opinions based on their notes
#         user_summaries = {user: summarize_user_opinions(notes) for user, notes in notes_by_user.items()}

#         # Return grouped notes by user
#         return {"summaries_by_user": user_summaries}

#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))


# @app.get("/recommend/{user_id}")
# async def recommend_users(user_id: str):
#     # Fetch all notes for the user to create a summary embedding
#     user_notes = (
#         client.query
#         .get(class_name, ["content"])
#         .with_where({
#             "path": ["user_id"],
#             "operator": "Equal",
#             "valueString": user_id
#         })
#         .do()
#     )
    
#     # Combine all user's notes for summarization
#     user_content = " ".join([note["content"] for note in user_notes["data"]["Get"][class_name]])
#     user_summary = summarize_user_opinions([user_content])
    
#     # Generate embedding for user summary
#     user_embedding = client.query.get(class_name, ["_additional { vector }"]).with_near_text({
#         "concepts": [user_summary]
#     }).do()
    
#     # Perform a search for similar users
#     similar_users = (
#         client.query
#         .get(class_name, ["user_id"])
#         .with_near_vector({
#             "vector": user_embedding["data"]["Get"][class_name][0]["_additional"]["vector"]
#         })
#         .with_limit(5)
#         .do()
#     )
