# CRUD Simulation Script
users = []

def create_user(name, email):
    user = {"id": len(users) + 1, "name": name, "email": email}
    users.append(user)
    return user

def read_users():
    return users

def update_user(user_id, name=None, email=None):
    for user in users:
        if user["id"] == user_id:
            if name: user["name"] = name
            if email: user["email"] = email
            return user
    return None

def delete_user(user_id):
    for i, user in enumerate(users):
        if user["id"] == user_id:
            return users.pop(i)
    return None

if __name__ == "__main__":
    # Test CRUD operations
    print("Creating users...")
    create_user("John Doe", "john@example.com")
    create_user("Jane Smith", "jane@example.com")
    
    print("All users:", read_users())
    
    print("Updating user 1...")
    update_user(1, name="John Updated")
    
    print("After update:", read_users())
    
    print("Deleting user 2...")
    delete_user(2)
    
    print("Final users:", read_users())