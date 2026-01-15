import requests
import sys

url = "https://jsonplaceholder.typicode.com/todos/1"


try:
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        print(f"Data: {data}")

        is_completed = data["completed"]

        if is_completed == False:
            print("ALARM: Task not completed!")

        else:
            print("System Stabil")
    
    else:
        print(f"Server returned an error:{response.status_code}")
            
except requests.exceptions.RequestException as e:
    print(f"An error occurred while making the request: {e}")

except Exception as e:
    print(f"An error occurred while connecting to the API: {e}")
    sys.exit(1)