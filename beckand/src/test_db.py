import sys
import os

# Adds the current directory to Python's search paths
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import save_user, create_tables
from security import hash_password

def init():
    create_tables()
    hashed = hash_password("1234")
    save_user("Giorgi", "Danelia", "giorgi@email.com", hashed, "Administrator")
    print("User successfully registered!")

if __name__ == "__main__":
    init()