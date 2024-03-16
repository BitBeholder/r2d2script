import os
from openai import OpenAI
from key import OPENAI_API_KEY

def get_greeting():

    client = OpenAI(api_key=OPENAI_API_KEY)
   
    try:
        chat_completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are an AI with a sense of humor, programmed to break the ice with people entering Startup Sauna."},
            {"role": "user", "content": "Come up with a light-hearted and humorous greeting that will make new visitors to Startup Sauna smile. The greeting can only be 8 words max."}
        ]
    )
        # Assuming the response structure is correctly handled by the library version
        greeting = chat_completion.choices[0].message.content.strip()  # Adjusted access to attributes
        return greeting
    except Exception as e:
        print(f"Error getting greeting from ChatGPT: {e}")
        return "Wazzup my homie. Welcome to Startup Sauna"
