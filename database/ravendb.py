from config import URLS, DB_NAME
from pyravendb.store import document_store

# Initialize RavenDB document store and define image-related functions
store = document_store.DocumentStore(URLS, DB_NAME)
store.initialize()