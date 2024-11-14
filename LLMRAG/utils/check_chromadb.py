import chromadb
import sys
import os

# Add the path to the parent directory containing the config module
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from config import Config

class CheckChromadb:
    def __init__(self):
        """
        Initializes the CheckChromadb class, setting up a persistent client for ChromaDB
        and managing collections. If there are more than 10 collections, the oldest one
        is deleted to maintain a maximum of 10 collections. The current collections are
        printed to the console.

        Attributes:
            client (PersistentClient): A persistent client for connecting to ChromaDB.
        """
        self.client = chromadb.PersistentClient(path=Config.MSDS_VECTOR_DB_PATH)
        
        # Get the list of collections
        collections = self.client.list_collections()
        
        # Check if the number of collections exceeds 5
        if len(collections) > 10:
            # Delete the first (oldest) collection
            oldest_collection = collections[0].name
            self.client.delete_collection(oldest_collection)
            print(f"Deleted oldest collection: {oldest_collection}")
        
        # Print all current collections
        for i, item in enumerate(self.client.list_collections()):
            print(f"Collection {i+1}: {item.name}")
