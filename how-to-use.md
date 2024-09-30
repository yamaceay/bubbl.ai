### HOW TO SETUP

Make sure Python 3.11 is installed on your local machine. MacOS is preferred. Then, run `pip3 install -r requirements.txt --upgrade` to install all packages. After that, set the following environment variables:

```bash
OPENAI_API_KEY=your-openai-api-key
WCS_API_KEY=your-weaviate-cluster-api-key
WCS_URL=your-weaviate-cluster-url
```

I prefer to store all environment variables in `.env` and run `pre.sh` to set them.After setting, you're ready to go. Just run `python3 bubblai.py` and enjoy!

### HOW TO USE

Below is a fun use case of the CLI app:

```log
INFO:httpx:HTTP Request: GET https://ew9mnqmvrne00rrfusz0q.c0.europe-west3.gcp.weaviate.cloud/v1/meta "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: GET https://pypi.org/pypi/weaviate-client/json "HTTP/1.1 200 OK"
✨ Welcome to Bubbl.ai! ✨
🌟 You are now a Bubbler! 🌟
INFO:httpx:HTTP Request: GET https://ew9mnqmvrne00rrfusz0q.c0.europe-west3.gcp.weaviate.cloud/v1/schema/Bubble "HTTP/1.1 200 OK"

💬 What would you like to do?
1. 💭 Enter write mode (create multiple bubbles)
2. 🗑️  Remove a single bubble
3. 🔍 Search bubbles by similarity (based on text)
4. 🔍 Search users by similarity (based on their summaries)
5. 📂 Insert bubbles from a JSON file
6. 🚨 Remove all bubbles (⚠️ with confirmation!)
7. 🚪 Exit
👉 Make your choice (1-7): 6
⚠️  Are you sure you want to delete **ALL** the bubbles by removing the schema? (yes/no): yes
🧼 Popping all the bubbles by deleting the 'Bubble' class schema...
INFO:httpx:HTTP Request: POST https://ew9mnqmvrne00rrfusz0q.c0.europe-west3.gcp.weaviate.cloud/v1/graphql "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: DELETE https://ew9mnqmvrne00rrfusz0q.c0.europe-west3.gcp.weaviate.cloud/v1/schema/Bubble "HTTP/1.1 200 OK"
💨 'Bubble' class schema deleted!
INFO:httpx:HTTP Request: GET https://ew9mnqmvrne00rrfusz0q.c0.europe-west3.gcp.weaviate.cloud/v1/schema/Bubble "HTTP/1.1 404 Not Found"
INFO:httpx:HTTP Request: POST https://ew9mnqmvrne00rrfusz0q.c0.europe-west3.gcp.weaviate.cloud/v1/schema "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: GET https://ew9mnqmvrne00rrfusz0q.c0.europe-west3.gcp.weaviate.cloud/v1/schema/Bubble "HTTP/1.1 200 OK"
Bubble collection created: _CollectionConfigSimple(name='Bubble', ...)
✨ 'Bubble' class schema has been re-created! You're ready to bubble again! 🫧

💬 What would you like to do?
1. 💭 Enter write mode (create multiple bubbles)
2. 🗑️  Remove a single bubble
3. 🔍 Search bubbles by similarity (based on text)
4. 🔍 Search users by similarity (based on their summaries)
5. 📂 Insert bubbles from a JSON file
6. 🚨 Remove all bubbles (⚠️ with confirmation!)
7. 🚪 Exit
👉 Make your choice (1-7): 5
📄 Enter the JSON file path: bubbles.json
Inserting bubbles from bubbles.json...
Bubbles inserted with UUIDs: {0: UUID('3656117b-f714-40fd-9625-c377deba6bb7'), 1: UUID('0dcb0bbe-72f3-4367-8df2-6703209f02d6'), ...,
48: UUID('e8b10ea9-1962-4d2d-8be3-509deab1933c'), 49: UUID('6a3ef6a6-f4d1-448c-b364-affb4b10575d')}

💬 What would you like to do?
1. 💭 Enter write mode (create multiple bubbles)
2. 🗑️  Remove a single bubble
3. 🔍 Search bubbles by similarity (based on text)
4. 🔍 Search users by similarity (based on their summaries)
5. 📂 Insert bubbles from a JSON file
6. 🚨 Remove all bubbles (⚠️ with confirmation!)
7. 🚪 Exit
👉 Make your choice (1-7): 2
Enter the UUID of the bubble to remove: 6a3ef6a6-f4d1-448c-b364-affb4b10575d
INFO:httpx:HTTP Request: DELETE https://ew9mnqmvrne00rrfusz0q.c0.europe-west3.gcp.weaviate.cloud/v1/objects/Bubble/6a3ef6a6-f4d1-448c-b364-affb4b10575d "HTTP/1.1 204 No Content"
Bubble with UUID 6a3ef6a6-f4d1-448c-b364-affb4b10575d removed successfully.

💬 What would you like to do?
1. 💭 Enter write mode (create multiple bubbles)
2. 🗑️  Remove a single bubble
3. 🔍 Search bubbles by similarity (based on text)
4. 🔍 Search users by similarity (based on their summaries)
5. 📂 Insert bubbles from a JSON file
6. 🚨 Remove all bubbles (⚠️ with confirmation!)
7. 🚪 Exit
👉 Make your choice (1-7): 1
Enter your username: yamac 

Write Mode: (Type your message below or type 'exit' to go back to the main menu)
Enter the content of the bubble (or 'exit' to finish): The mankind went too far away from its nature, why don't we go back to the traditional gender roles?
Enter the category of the bubble: Dating   

Write Mode: (Type your message below or type 'exit' to go back to the main menu)
Enter the content of the bubble (or 'exit' to finish): AfD is a Neonazi party in Germany, which wants to deport all people of different cultural background to other countries, even though they feel at home in Germany. Germany doesn't learn from its mistakes.
Enter the category of the bubble: Political

Write Mode: (Type your message below or type 'exit' to go back to the main menu)
Enter the content of the bubble (or 'exit' to finish): I believe that we'll reach the end of the Moore's Law soon, and this will be the end of the disruptive hi-tech industry.    
Enter the category of the bubble: Technology

Write Mode: (Type your message below or type 'exit' to go back to the main menu)
Enter the content of the bubble (or 'exit' to finish): exit
Inserting all bubbles...
Bubbles inserted with UUIDs: {0: UUID('0a1e2679-404c-4e13-8000-27a7b1f7f688'), 1: UUID('17c9ca78-585d-48e4-8e2f-2ae396e82635'), 2: UUID('92344bbf-d4ed-4c80-9f87-e15f92a7c72f')}

💬 What would you like to do?
1. 💭 Enter write mode (create multiple bubbles)
2. 🗑️  Remove a single bubble
3. 🔍 Search bubbles by similarity (based on text)
4. 🔍 Search users by similarity (based on their summaries)
5. 📂 Insert bubbles from a JSON file
6. 🚨 Remove all bubbles (⚠️ with confirmation!)
7. 🚪 Exit
👉 Make your choice (1-7): 3
Enter your search query: Moore's Law
Enter the number of bubble results to return: 5
INFO:root:Querying top 5 most relevant bubbles for text: 'Moore's Law'...
1. Content: I believe that we'll reach the end of the Moore's Law soon, and this will be the end of the disruptive hi-tech industry., User: yamac, Category: Technology
2. Content: Quantum supremacy will change how we think about computational limits., User: user5, Category: Technology
3. Content: Quantum entanglement could revolutionize communication systems., User: user5, Category: Technology
4. Content: Quantum computers can solve problems that are impossible for classical computers., User: user5, Category: Technology
5. Content: Neural networks and deep learning will continue to advance AI capabilities., User: user8, Category: Technology

💬 What would you like to do?
1. 💭 Enter write mode (create multiple bubbles)
2. 🗑️  Remove a single bubble
3. 🔍 Search bubbles by similarity (based on text)
4. 🔍 Search users by similarity (based on their summaries)
5. 📂 Insert bubbles from a JSON file
6. 🚨 Remove all bubbles (⚠️ with confirmation!)
7. 🚪 Exit
👉 Make your choice (1-7): 4
Enter your search query: The world proceeds in a very fast pace, and I wonder if we'll be able to catch up everything. Hi-tech is faster than ever.
Enter the number of results to return: 10
INFO:root:Querying top 10 most relevant bubbles for text: 'The world proceeds in a very fast pace, and I wonder if we'll be able to catch up everything. Hi-tech is faster than ever.'...
INFO:root:Grouping bubbles by user...
INFO:root:Summarizing user content...
INFO:root:Embedding text with OpenAI: The world proceeds in a very fast pace, and I wond...
INFO:httpx:HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
INFO:root:Embedding user summaries...
INFO:root:Embedding text with OpenAI: I believe that we'll reach the end of the Moore's ...
INFO:httpx:HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
INFO:root:Embedding text with OpenAI: Quantum supremacy will change how we think about c...
INFO:httpx:HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
INFO:root:Embedding text with OpenAI: AI will redefine the nature of work in the 21st ce...
INFO:httpx:HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
INFO:root:Embedding text with OpenAI: Artificial intelligence will revolutionize healthc...
INFO:httpx:HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
INFO:root:Computing cosine similarity between users and the query...
Ranked Users by Opinion Alignment:
1. User: yamac, Similarity: 84.69%
2. User: user5, Similarity: 81.71%
3. User: user8, Similarity: 80.56%
4. User: user1, Similarity: 79.19%

💬 What would you like to do?
1. 💭 Enter write mode (create multiple bubbles)
2. 🗑️  Remove a single bubble
3. 🔍 Search bubbles by similarity (based on text)
4. 🔍 Search users by similarity (based on their summaries)
5. 📂 Insert bubbles from a JSON file
6. 🚨 Remove all bubbles (⚠️ with confirmation!)
7. 🚪 Exit
👉 Make your choice (1-7): 7
✨ Thanks for bubbling with us! Until next time! ✨
INFO:root:Closed Weaviate client connection.
```