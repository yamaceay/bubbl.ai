
### How to Use Command-Line Interface?

Below is a fun use case of the CLI app:

```log
INFO:httpx:HTTP Request: GET https://ew9mnqmvrne00rrfusz0q.c0.europe-west3.gcp.weaviate.cloud/v1/meta "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: GET https://pypi.org/pypi/weaviate-client/json "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: GET https://ew9mnqmvrne00rrfusz0q.c0.europe-west3.gcp.weaviate.cloud/v1/schema/Bubble "HTTP/1.1 200 OK"
INFO:root:Bubble collection already exists.
✨ 🌟 Welcome to Bubbl.ai! 🌟
💭 You're about to dive into the world of bubbles – your thoughts, ideas, and musings all wrapped up in one fun, floating place!

🎈 What bubbly adventure would you like to embark on today?
1. 💭 Blow a new Bubble (Insert a Bubble)
2. 🔍 Explore Bubbles (Search Bubbles)
3. 🔍 Find Like-minded Bubblers (Search Users by Similarity)
4. 🗑️  Pop a Bubble (Remove a Bubble)
5. 📂 Blow Bubbles from JSON (Insert Bubbles from a JSON file)
6. 🚨 Pop ALL the Bubbles (Remove All Bubbles with Confirmation)
7. 🚪 Exit Bubbl.ai
👉 Make your bubbly choice (1-7): 1
💬 Let's blow a new bubble! 🎈
Enter your bubbly username: yamac
What's on your mind? Tell me and I'll bubble it up: All around the globe, wars come and go. The only thing that remains unchanged is the corruptness of the global politics.
How would you categorize this bubble (e.g., Technology, Life, Fun). Press ENTER to skip: Politics
INFO:root:Inserting bubbles into the database...
💬 Bubbles inserted with IDs: {0: UUID('69a77635-7f6f-4393-9468-48ce759a725f')}
🫧 ✨ Your thoughts are now safely floating as a bubble! ✨

🎈 What bubbly adventure would you like to embark on today?
1. 💭 Blow a new Bubble (Insert a Bubble)
2. 🔍 Explore Bubbles (Search Bubbles)
3. 🔍 Find Like-minded Bubblers (Search Users by Similarity)
4. 🗑️  Pop a Bubble (Remove a Bubble)
5. 📂 Blow Bubbles from JSON (Insert Bubbles from a JSON file)
6. 🚨 Pop ALL the Bubbles (Remove All Bubbles with Confirmation)
7. 🚪 Exit Bubbl.ai
👉 Make your bubbly choice (1-7): 2
💬 Ready to explore the bubbly world? Let's find some relevant bubbles! 🔍
Enter your search query: Global politics is corrupt
How many bubbles would you like to see? (Enter a number): 5
INFO:root:Querying top 5 most relevant bubbles for text: 'Global politics is corrupt'...
🫧 Relevant Bubbles:
💬 All around the globe, wars come and go. The only thing that remains unchanged is the corruptness of the global politics. (User: yamac, Category: Politics)
💬 Global trade agreements need to be rewritten for the digital age. (User: user7, Category: Economics)
💬 Global cooperation is needed to address the challenges of climate change. (User: user10, Category: Environment)
💬 AI ethics and governance will be critical in the coming decades. (User: user8, Category: Technology)
💬 Blockchain can enhance transparency in government systems. (User: user3, Category: Technology)

🎈 What bubbly adventure would you like to embark on today?
1. 💭 Blow a new Bubble (Insert a Bubble)
2. 🔍 Explore Bubbles (Search Bubbles)
3. 🔍 Find Like-minded Bubblers (Search Users by Similarity)
4. 🗑️  Pop a Bubble (Remove a Bubble)
5. 📂 Blow Bubbles from JSON (Insert Bubbles from a JSON file)
6. 🚨 Pop ALL the Bubbles (Remove All Bubbles with Confirmation)
7. 🚪 Exit Bubbl.ai
👉 Make your bubbly choice (1-7): 3
💬 Let's find other Bubblers who think like you! 🫂
Enter your search query: Technological advancements are at a high pace
How many bubbles would you like to see? (Enter a number): 10
INFO:root:Querying top 10 most relevant bubbles for text: 'Technological advancements are at a high pace'...
INFO:root:Grouping bubbles by user...
INFO:root:Summarizing user content...
INFO:root:Embedding text with OpenAI: Technological advancements are at a high pace...
INFO:httpx:HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
INFO:root:Embedding user summaries...
INFO:root:Embedding text with OpenAI: Neural networks and deep learning will continue to...
INFO:httpx:HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
INFO:root:Embedding text with OpenAI: Artificial intelligence will revolutionize healthc...
INFO:httpx:HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
INFO:root:Embedding text with OpenAI: Quantum supremacy will change how we think about c...
INFO:httpx:HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
INFO:root:Computing cosine similarity between users and the query...
🎈 Bubblers with similar thoughts:
👤 User: user8, Similarity: 83.12%
👤 User: user1, Similarity: 81.72%
👤 User: user5, Similarity: 81.41%

🎈 What bubbly adventure would you like to embark on today?
1. 💭 Blow a new Bubble (Insert a Bubble)
2. 🔍 Explore Bubbles (Search Bubbles)
3. 🔍 Find Like-minded Bubblers (Search Users by Similarity)
4. 🗑️  Pop a Bubble (Remove a Bubble)
5. 📂 Blow Bubbles from JSON (Insert Bubbles from a JSON file)
6. 🚨 Pop ALL the Bubbles (Remove All Bubbles with Confirmation)
7. 🚪 Exit Bubbl.ai
👉 Make your bubbly choice (1-7): 4
💬 Time to pop a bubble! 🗑️
Enter the UUID of the bubble you'd like to pop: 69a77635-7f6f-4393-9468-48ce759a725f
INFO:root:Removing bubble with UUID 69a77635-7f6f-4393-9468-48ce759a725f...
INFO:httpx:HTTP Request: DELETE https://ew9mnqmvrne00rrfusz0q.c0.europe-west3.gcp.weaviate.cloud/v1/objects/Bubble/69a77635-7f6f-4393-9468-48ce759a725f "HTTP/1.1 204 No Content"
INFO:root:Bubble with UUID 69a77635-7f6f-4393-9468-48ce759a725f removed successfully.
🎉 ✨ Bubble with UUID 69a77635-7f6f-4393-9468-48ce759a725f has been successfully popped! ✨

🎈 What bubbly adventure would you like to embark on today?
1. 💭 Blow a new Bubble (Insert a Bubble)
2. 🔍 Explore Bubbles (Search Bubbles)
3. 🔍 Find Like-minded Bubblers (Search Users by Similarity)
4. 🗑️  Pop a Bubble (Remove a Bubble)
5. 📂 Blow Bubbles from JSON (Insert Bubbles from a JSON file)
6. 🚨 Pop ALL the Bubbles (Remove All Bubbles with Confirmation)
7. 🚪 Exit Bubbl.ai
👉 Make your bubbly choice (1-7): 6
💬 ⚠️ Are you sure you want to pop ALL the bubbles? This action is irreversible! ⚠️
Type 'yes' if you're absolutely sure: yes
INFO:root:🧼 Popping all the bubbles by deleting the 'Bubble' class schema...
INFO:httpx:HTTP Request: POST https://ew9mnqmvrne00rrfusz0q.c0.europe-west3.gcp.weaviate.cloud/v1/graphql "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: DELETE https://ew9mnqmvrne00rrfusz0q.c0.europe-west3.gcp.weaviate.cloud/v1/schema/Bubble "HTTP/1.1 200 OK"
INFO:root:💨 'Bubble' class has been deleted!
INFO:httpx:HTTP Request: GET https://ew9mnqmvrne00rrfusz0q.c0.europe-west3.gcp.weaviate.cloud/v1/schema/Bubble "HTTP/1.1 404 Not Found"
INFO:httpx:HTTP Request: POST https://ew9mnqmvrne00rrfusz0q.c0.europe-west3.gcp.weaviate.cloud/v1/schema "HTTP/1.1 200 OK"
INFO:root:Bubble collection created
INFO:httpx:HTTP Request: GET https://ew9mnqmvrne00rrfusz0q.c0.europe-west3.gcp.weaviate.cloud/v1/schema/Bubble "HTTP/1.1 200 OK"
INFO:root:✨ 'Bubble' class has been re-created! You're ready to bubble again! 🫧
💬 💨 Poof! All bubbles have been popped, and the slate is clean! 🫧

🎈 What bubbly adventure would you like to embark on today?
1. 💭 Blow a new Bubble (Insert a Bubble)
2. 🔍 Explore Bubbles (Search Bubbles)
3. 🔍 Find Like-minded Bubblers (Search Users by Similarity)
4. 🗑️  Pop a Bubble (Remove a Bubble)
5. 📂 Blow Bubbles from JSON (Insert Bubbles from a JSON file)
6. 🚨 Pop ALL the Bubbles (Remove All Bubbles with Confirmation)
7. 🚪 Exit Bubbl.ai
👉 Make your bubbly choice (1-7): 5
💬 Time to blow some bubbles from a JSON file! 🎈
Enter the path to your bubbly JSON file: bubbles.json
💬 Bubbles inserted with IDs: {0: UUID('6f1aec66-876a-4f01-a0ce-fd51cb8de934'), 1: UUID('8b527829-9e20-48f5-9e26-6ea8a82e5052'), 2: UUID('64253b6b-ccb3-4084-a2fe-53d99b04097a'), ..., 49: UUID('05681b7c-3ea4-4ac3-96fa-cb185eca3c82')}
💬 🎉 Bubbles from the JSON file are now floating in Bubbl.ai! 🎉

🎈 What bubbly adventure would you like to embark on today?
1. 💭 Blow a new Bubble (Insert a Bubble)
2. 🔍 Explore Bubbles (Search Bubbles)
3. 🔍 Find Like-minded Bubblers (Search Users by Similarity)
4. 🗑️  Pop a Bubble (Remove a Bubble)
5. 📂 Blow Bubbles from JSON (Insert Bubbles from a JSON file)
6. 🚨 Pop ALL the Bubbles (Remove All Bubbles with Confirmation)
7. 🚪 Exit Bubbl.ai
👉 Make your bubbly choice (1-7): 7
👋 Thank you for visiting Bubbl.ai! Until next time, keep your thoughts floating! ✨
```