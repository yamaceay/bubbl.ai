import weaviate
import json

client = weaviate.Client("http://localhost:8080/")  # Replace with your Weaviate endpoint

# we will create the class "Question"
class_obj = {
    "class": "Question",
    "description": "Information from a Jeopardy! question",  # description of the class
    "properties": [
        {
            "name": "question",
            "dataType": ["text"],
            "description": "The question",
        },
        {
            "name": "answer",
            "dataType": ["text"],
            "description": "The answer",
        },
        {
            "name": "category",
            "dataType": ["text"],
            "description": "The question category",
        },
    ],
    "vectorizer": "text2vec-openai",
    "moduleConfig": {
        "generative-openai": {}  # Set `generative-openai` as the generative module
    }
}

# # add the schema
# client.schema.create_class(class_obj)

# # get the schema
# schema = client.schema.get()

# # print the schema
# print(json.dumps(schema, indent=4))

# ===== import data =====
# Load data
# uuid = client.data_object.create(
#     class_name="JeopardyQuestion",
#     data_object={
#         "question": "This vector DB is OSS & supports automatic property type inference on import",
#         # "answer": "Weaviate",  # schema properties can be omitted
#         "newProperty": 123,  # will be automatically added as a number property
#     }
# )

# print(uuid)  # the return value is the object's UUID

data_object = client.data_object.get_by_id(
    "9e990bfa-8e82-4ddb-a86d-d568c59852f4",
    # class_name="JeopardyQuestion",
    with_vector=True,
)

print(json.dumps(data_object, indent=2))