from ui.app_window import SDLHApplication
from database.connection import initialize_database
from utils.logging_config import configure_logging

if __name__ == "__main__":
    configure_logging()
    initialize_database()
    SDLHApplication().run()
