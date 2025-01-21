from auth import get_password_hash, USERS

def create_user(email: str, password: str):
    hashed_password = get_password_hash(password)
    USERS[email] = {
        "email": email,
        "hashed_password": hashed_password
    }
    print(f"\nUser created successfully!")
    print(f"Email: {email}")
    print(f"Hashed password: {hashed_password}")
    print("\nAdd this to your USERS dictionary in auth.py:")
    print(f"""    "{email}": {{
        "email": "{email}",
        "hashed_password": "{hashed_password}"
    }},""")

if __name__ == "__main__":
    email = input("Enter email: ")
    password = input("Enter password: ")
    create_user(email, password) 