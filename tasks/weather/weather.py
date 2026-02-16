from dotenv import load_dotenv
import os
import json
from groq import Groq


load_dotenv()
client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)


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
    model_name = "llama-3.3-70b-versatile"
    user_prompt = "Şu anki güncel veriye göre İstanbul'da hava durumu nedir?"

    messages = [
        {
            "role": "system", 
            "content": "You are a factual assistant. Use the provided tool outputs strictly to answer questions."
        },
        {
            "role": "user",
            "content": user_prompt
        }
    ]

    # Step 1: Initial Request
    response = client.chat.completions.create(
        model=model_name,
        messages=messages,
        tools=tools,
        tool_choice="auto"
    )

    response_message = response.choices[0].message
    tool_calls = response_message.tool_calls

    if tool_calls:
        # 1. ÖNEMLİ: Assistant'ın tool_call mesajını geçmişe BİR KEZ ekle.
        messages.append(response_message)

        for tool_call in tool_calls:
            function_name = tool_call.function.name
            function_args = json.loads(tool_call.function.arguments)

            if function_name == "get_weather":
                # 2. Fonksiyonu çalıştır
                function_response = get_weather(city=function_args.get("city"))
                
                # 3. ÖNEMLİ: Sadece tool sonucunu ekle (response_message'ı tekrar ekleme!)
                messages.append({
                    "tool_call_id": tool_call.id,
                    "role": "tool",
                    "name": function_name,
                    "content": function_response
                })

        # Step 2: Final Request with all information
        final_response = client.chat.completions.create(
            model=model_name,
            messages=messages,
            temperature=0 # Gerçekçi ve net sonuç için 0
        )
        
        print("\nFinal AI Answer:")
        print(final_response.choices[0].message.content)
    else:
        print(response_message.content)

run_poc()

