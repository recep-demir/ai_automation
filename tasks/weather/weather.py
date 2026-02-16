from dotenv import load_dotenv
import os
import json
from groq import Groq

# 1. Environment Setup
load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# 2. Tool Definition
def get_weather(city):
    """Gerçek fonksiyonumuz."""
    print(f"\n[SYSTEM LOG] get_weather fonksiyonu '{city}' için çalıştı...") # Debug Log
    weather_data = {
        "istanbul": "22°C, Sunny",
        "zurich": "12°C, Rainy",
        "london": "15°C, Cloudy"
    }
    result = weather_data.get(city.lower(), "Unknown Location")
    print(f"[SYSTEM LOG] Dönen Sonuç: {result}\n") # Debug Log
    return result

tools = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get the current weather for a specific city.",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": "The name of the city (e.g. Istanbul)"
                    }
                },
                "required": ["city"]
            }
        }
    }
]

# 3. Execution Logic
def run_poc():
    model_name = "llama-3.3-70b-versatile"
    user_prompt = "İstanbul'da hava durumu nedir?"

    # Context (Message History) Başlatılıyor
    messages = [
        {
            "role": "system",
            "content": "You are a helpful assistant. If a tool returns a value, YOU MUST use that value to answer. Do not say you cannot access data."
        },
        {
            "role": "user",
            "content": user_prompt
        }
    ]

    print("--- 1. AI Çağrısı Yapılıyor ---")
    response = client.chat.completions.create(
        model=model_name,
        messages=messages,
        tools=tools,
        tool_choice="auto"
    )

    response_message = response.choices[0].message
    tool_calls = response_message.tool_calls

    if tool_calls:
        print("AI: 'Bir araca (Tool) ihtiyacım var.'")
        
        # --- KRİTİK ADIM 1: AI'nın isteğini (Request) geçmişe ekle ---
        # Bu adım DÖNGÜNÜN DIŞINDA olmalı. AI'nın "Ben şunu istedim" dediği kayıttır.
        messages.append(response_message)

        for tool_call in tool_calls:
            function_name = tool_call.function.name
            function_args = json.loads(tool_call.function.arguments)
            
            print(f"Calling Function: {function_name} with args: {function_args}")

            if function_name == "get_weather":
                function_response = get_weather(city=function_args.get("city"))
                
                # --- KRİTİK ADIM 2: Aracın cevabını (Response) geçmişe ekle ---
                # Burada 'tool_call_id' ÇOK ÖNEMLİDİR. AI bu ID ile cevabı eşleştirir.
                messages.append({
                    "tool_call_id": tool_call.id,
                    "role": "tool",
                    "name": function_name,
                    "content": function_response,
                })

        # --- DEBUG ADIMI: AI'ya gitmeden önceki son listeyi görelim ---
        # print(json.dumps(messages, indent=2, default=str)) 
        
        print("--- 2. AI Çağrısı (Final Cevap) Yapılıyor ---")
        final_response = client.chat.completions.create(
            model=model_name,
            messages=messages,
            temperature=0.1 # Düşük yaratıcılık = Yüksek sadakat
        )
        
        print("\nFinal AI Answer:")
        print(final_response.choices[0].message.content)

    else:
        print("AI herhangi bir araç kullanmak istemedi.")
        print(response_message.content)

if __name__ == "__main__":
    run_poc()