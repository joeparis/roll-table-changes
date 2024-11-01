import json
import os
import re

# Directory containing JSON files
folder_path = "src"

# Pattern to match strings starting with "Aeon Stone"
pattern = r"^Aeon Stone.*"

# Loop through all JSON files in the folder
for filename in os.listdir(folder_path):
    if filename.endswith(".json"):
        file_path = os.path.join(folder_path, filename)

        # Open and load the JSON file
        with open(file_path, "r", encoding="utf-8") as file:
            try:
                data = json.load(file)
            except json.JSONDecodeError:
                print(f"Could not decode JSON in file: {file_path}")
                continue

            # Recursively search for matches in the JSON data
            def search_in_json(data):
                if isinstance(data, dict):
                    for key, value in data.items():
                        if isinstance(value, (str, dict, list)):
                            search_in_json(value)
                elif isinstance(data, list):
                    for item in data:
                        if isinstance(item, (str, dict, list)):
                            search_in_json(item)
                elif isinstance(data, str):
                    if re.match(pattern, data):
                        print(f"Found in {filename}: {data}")

            search_in_json(data)
