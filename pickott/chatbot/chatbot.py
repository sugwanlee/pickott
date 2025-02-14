import openai
import os
openai.api_key = os.environ.get("OPENAI_API_KEY")

def chat_call(user_input):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
                {"role": "system", "content": "You are a movie referrer in Korea."},
                {"role": "user", "content": user_input}
            ]
        )

    return response['choices'][0]['message']['content']