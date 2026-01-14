import sys

# Check command line arguments
# Usage: python script.py user_name
if len(sys.argv) > 1:
    user_name = sys.argv[1]
    print(f"Welcome to IT Operations, {user_name}!")

elif (len(sys.argv) > 1 and (sys.argv[1] == "admin")):
    print(f"Welcome to IT Operations, admin!")

else:
    print("Error: Please provide a username.")
    sys.exit() # Stop the execution

# Check Python version
print(f"Python Version: {sys.version}")