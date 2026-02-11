from dotenv import load_dotenv
import os
import json
from groq import Groq


load_dotenv()
client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)
model_name = "llama-3.3-70b-versatile"

def get_weather(city):

    weather_data = {
        "istanbul": "22°C, Sunny",
        "zurich": "12°C, Rainy",
        "london": "15°C, Cloudy"
    }
    result = weather_data.get(city.lower(), "Weather information not found for this location.")
    return result

tools = [
    {
        "type" :"function",
        "function" :{
            "name" : "get_weather",
            "description": "Get the current weather for a specific city.",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": "The name of the city to get the weather for."
                    }
                },
                "required": ["city"]
            }
        

        }
    }
]


def run_poc():
    user_prompt = "İstanbul'da hava nasıl?"


    messages = [
        {
            "role": "user",
            "content": user_prompt
        }
    ]

    response = client.chat.completions.create(
        model= model_name,
        messages=messages,
        tools=tools,
        tool_choice="auto"
    )

    response_message = response.choices[0].message
    tool_calls = response_message.tool_calls

    if tool_calls:
        print("AI: 'I need to call a function to answer this.'")

        for tool_call in tool_calls:
            function_name = tool_call.function.name
            function_args = json.loads(tool_call.function.arguments)

            print(f"Calling Function: {function_name} with arguments: {function_args}")

            if function_name == "get_weather":
                function_response = get_weather(
                    city=function_args.get("city")
                )
                messages.append(response_message) # Add the model's call request to history
                messages.append({
                    "tool_call_id": tool_call.id,
                    "role": "tool",
                    "name": function_name,
                    "content": function_response
                })


        final_response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages
        )
        
        print("\nFinal AI Answer:")
        print(final_response.choices[0].message.content)

    else:
        print(response_message.content)



run_poc()

