import inspect
import json
import os


def check_duplicate_keys(data):
    seen_keys = set()

    def check_dict(dictionary, path=""):
        for key, value in dictionary.items():
            current_path = f"{path}.{key}" if path else key
            if current_path in seen_keys:
                print(f"Duplicate key found: {current_path}")
            seen_keys.add(current_path)

            if isinstance(value, dict):
                check_dict(value, path=current_path)

    for category, category_data in data.items():
        print(f"Checking category: {category}")
        for item in category_data:
            check_dict(item, path=f"{category}_item")


if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(script_dir, "api_endpoint_config.json")

    with open(file_path, "r") as file:
        json_data = json.load(file)

    check_duplicate_keys(json_data)
