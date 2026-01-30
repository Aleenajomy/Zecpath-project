import json

def write_json(data, filename):
    with open(filename, 'w') as f:
        json.dump(data, f, indent=2)
    print(f"Data written to {filename}")

def read_json(filename):
    try:
        with open(filename, 'r') as f:
            data = json.load(f)
        print(f"Data read from {filename}")
        return data
    except FileNotFoundError:
        print(f"File {filename} not found")
        return None

if __name__ == "__main__":
    # Sample data
    sample_data = {
        "users": [
            {"id": 1, "name": "Alice", "role": "admin"},
            {"id": 2, "name": "Bob", "role": "user"}
        ],
        "settings": {
            "theme": "dark",
            "notifications": True
        }
    }
    
    # Write JSON
    write_json(sample_data, "sample_data.json")
    
    # Read JSON
    loaded_data = read_json("sample_data.json")
    print("Loaded data:", loaded_data)