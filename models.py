from flask_login import LoginManager, UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

# Define the User class
class User(UserMixin):
    def __init__(self, id, username, password):
        self.id = id
        self.username = username
        self.password = password

    @staticmethod
    def get(user_id):
        # Access the global 'users' dictionary to fetch the user by ID
        return users.get(user_id)

    def check_password(self, password):
        # Check if the hashed password matches
        return check_password_hash(self.password, password)

# User data storage (example in-memory storage)
users = {
    1: User(id=1, username="user", password=generate_password_hash("password"))
}

# Initialize LoginManager
login_manager = LoginManager()

# User loader function for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    # Fetch the user by ID from the 'users' dictionary
    return User.get(int(user_id))  # Make sure to cast user_id to int if needed