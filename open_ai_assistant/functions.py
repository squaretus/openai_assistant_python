import json
import os
import openai
from openai import OpenAI

def create_assistant(client):
    """Uses existing assistant_id if assistant.json file is present or
    creates a new assistant with files existing in learning_base directory
    and returns it assistant_id"""
    assistant_file_path = 'assistant.json'
    files_names = []
    files = []
    files_ids = []

    if os.path.exists(assistant_file_path):
        with open(assistant_file_path, mode="r", encoding="utf-8") as file:
            assistant_data = json.load(file)
            assistant_id = assistant_data['assistant_id']
            print("Loaded existing assistant ID.")
    else:
        for file_name in os.listdir("learning_base"):
            if os.path.isfile(f"learning_base/{file_name}"):
                files_names.append(file_name)

        for name in files_names:
            with open(f"learning_base/{name}", "rb") as file:
                files.append(file)

    for file_object in files:
        file = client.files.create(file=file_object, purpose='assistants')

        files_ids.append(file.id)

    assistant = client.beta.assistants.create(name="Master of Popcorn",
                                              instructions="""You were created to help new employees learn how to make popcorn.
                                              They will ask you questions about the method of making popcorn, as well as about grams for different models of devices.
                                              You must answer clearly and concisely.
                                              When asking questions about grams, be sure to provide the full information specified in the instructions given to you in the files.
                                              Also ask the user what kind of popcorn he wants to make, if he hasn’t specified.
                                              And also ask about the type of machine (Robopop or Classic machine) and the caramelizer model if it should be determined for this type of popcorn""",
                                              model="gpt-3.5-turbo-1106",
                                              tools=[{
                                                  "type": "retrieval"
                                              }],
                                              file_ids=files_ids)

    assistant_id = assistant.id

    with open(assistant_file_path, mode="w", encoding="utf-8") as file:
        json.dump({'assistant_id': assistant_id}, file)
        print("Created a new assistant and saved the ID.")


    return assistant_id
