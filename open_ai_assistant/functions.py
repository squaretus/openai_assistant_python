import json
import os
import openai
from openai import OpenAI

caramel_robopop=open("learning_base/Карамельный_Робопоп.pdf", "rb")
caramel_colorized_robopop=open("learning_base/Карамельный_ЦВЕТНОЙ_Робопоп.pdf", "rb")
caramel_colorized_gold_medal=open("learning_base/Карамельный_ЦВЕТНОЙ_Gold_Medal.pdf", "rb")
caramel_colorized_robosugar=open("learning_base/Карамельный_ЦВЕТНОЙ_RoboSugar.pdf", "rb")
caramel_gold_medal=open("learning_base/Карамельный_Gold_Medal.pdf", "rb")
caramel_robosugar=open("learning_base/Карамельный_RoboSugar.pdf", "rb")
sweety_popcorn=open("learning_base/Сладкий_попкорн.pdf", "rb")
salty_popcorn=open("learning_base/Соленый_попкорн.pdf", "rb")
cheesy_popcorn_caramelizator=open("learning_base/Сырный_попкорн_(Карамелизатор).pdf", "rb")
cheesy_popcorn_couter=open("learning_base/Сырный_попкорн_(Коутер).pdf", "rb")

files = [caramel_robopop,
         caramel_colorized_robopop,
         caramel_colorized_gold_medal,
         caramel_colorized_robosugar,
         caramel_gold_medal,
         caramel_robosugar,
         sweety_popcorn,
         salty_popcorn,
         cheesy_popcorn_caramelizator,
         cheesy_popcorn_couter]

def create_assistant(client):
  assistant_file_path = 'assistant.json'

  if os.path.exists(assistant_file_path):
    with open(assistant_file_path, 'r') as file:
      assistant_data = json.load(file)
      assistant_id = assistant_data['assistant_id']
      print("Loaded existing assistant ID.")
  else:
    files_ids = []

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

    with open(assistant_file_path, 'w') as file:
      json.dump({'assistant_id': assistant_id}, file)
      print("Created a new assistant and saved the ID.")


  return assistant_id
