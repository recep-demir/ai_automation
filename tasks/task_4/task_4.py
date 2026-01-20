import requests  # Import the library for making HTTP requests (GET, POST, etc.)
import sys       # Import the system module for exit codes and environment interaction

# Define the API endpoint URL (JSONPlaceholder is a mock API for testing)
url = "https://jsonplaceholder.typicode.com/todos/1"

try:
    # Perform a GET request to the specified URL to fetch data
    response = requests.get(url)

    # Check if the HTTP status code is 200 (OK) which means the request was successful
    if response.status_code == 200:
        # Parse the response body as a JSON object (converts it to a Python dictionary)
        data = response.json()
        print(f"Data: {data}")

        # Extract the value associated with the "completed" key
        is_completed = data["completed"]

        # Conditional logic based on the status of the task
        if not is_completed:
            # Trigger an alert if the task is not yet finished
            print("ALARM: Task not completed!")
        else:
            # Confirm that the process or task is successful
            print("System Stabil")
    
    else:
        # Handle cases where the server reached but returned an error code (e.g., 404, 500)
        print(f"Server returned an error: {response.status_code}")
            
# Specifically catch network-related issues (DNS failure, connection timeout, etc.)
except requests.exceptions.RequestException as e:
    print(f"An error occurred while making the request: {e}")

# Catch any other unexpected errors to prevent the script from crashing silently
except Exception as e:
    print(f"An error occurred while connecting to the API: {e}")
    sys.exit(1) # Terminate the script with a non-zero exit status indicating an error