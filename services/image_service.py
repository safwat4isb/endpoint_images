from PIL import Image
from io import BytesIO
from models import ImageData
from database.ravendb import store

# Function to calculate image width and height
def calculate_image_dimensions(image_bytes):
    image = Image.open(BytesIO(image_bytes))
    width, height = image.size
    return width, height


# Function to save image data in RavenDB
def save_image_data(image_data:ImageData):
    with store.open_session() as session:
        session.store(image_data)
        session.save_changes()
        