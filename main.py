from fastapi import FastAPI, UploadFile, File, HTTPException
from PIL import Image
from io import BytesIO
import base64
from pydantic import BaseModel
import uuid
from pyravendb.store import document_store


# Initialize RavenDB document store with certificate
URLS = ["http://127.0.0.1:8080"]
DB_NAME = "images"
# CERT_PATH = "C:/Users/safwa/Desktop/RavenDB-6.0.100-windows-x64/safwa.Cluster.Settings 2024-02-15 20-15/admin.client.certificate.safwa.pfx"
# Initialize RavenDB document store
store = document_store.DocumentStore(URLS, DB_NAME)
# store.certificate_pem_path = CERT_PATH
store.initialize()

# Define RavenDB model for storing image data
class ImageDataModel:
    def __init__(self, image_path, width, height):
        self.image_path = image_path
        self.width = width
        self.height = height


app = FastAPI()

class ImageData(BaseModel):
    base64_string: str

# Function to calculate image width and height
def calculate_image_dimensions(image_bytes):
    image = Image.open(BytesIO(image_bytes))
    width, height = image.size
    return width, height
# Function to calculate image dimensions
def calculate_image_dimensions_base64(base64_string):
    image_bytes = base64.b64decode(base64_string)
    image = Image.open(BytesIO(image_bytes))
    width, height = image.size
    return width, height

# Function to save image data in RavenDB
def save_image_data(image_path, width, height):
    image_data = ImageDataModel(image_path, width, height)
    with store.open_session() as session:
        session.store(image_data)
        session.save_changes()
        
# POST endpoint to accept image file upload
@app.post("/upload/")
async def upload_image(file: UploadFile = File(...)):
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Uploaded file is not an image.")

    image_bytes = await file.read()
    width, height = calculate_image_dimensions(image_bytes)
    # Convert image to base64
    base64_image = base64.b64encode(image_bytes).decode("utf-8")
    save_image_data(file.filename, width, height)
    return {"image": base64_image, "width": width, "height": height}

   

# POST endpoint to accept image in base64 and return processed image
@app.post("/process-image/")
async def process_image(image_data: ImageData):
    try:
        width, height = calculate_image_dimensions_base64(image_data.base64_string)
       

        # Return the processed image as base64
        return {
            "width": width,
            "height": height,
            "base64_image": image_data.base64_string
           
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error processing image: {str(e)}")

# GET endpoint to generate a random UUID for the given user name
@app.get("/api/{user_name}")
async def get_uuid(user_name: str):
    # Generate a random UUID
    random_uuid = uuid.uuid4()
    return {"user_name": user_name, "uuid": str(random_uuid)}



# GET endpoint to retrieve image properties from RavenDB
@app.get("/image_properties/{image_id}")
async def get_image_properties(image_id: str):
    try:
        full_document_id = f"ImageDataModels/{image_id}"
        with store.open_session() as session:
            # Load the document by its ID
            result = session.load(full_document_id)
            
            # Check if the document exists
            if result is not None:
                # Extract image properties
                image_path = result.image_path
                width = result.width
                height = result.height
                
                # Return image properties
                return {
                    "image_id": image_id,
                    "image_path": image_path,
                    "width": width,
                    "height": height
                }
            else:
                # If the document doesn't exist, raise HTTPException with status code 404
                raise HTTPException(status_code=404, detail="Image not found")
    except Exception as e:
        # If any error occurs during the process, raise HTTPException with status code 400
        raise HTTPException(status_code=400, detail=f"Error retrieving image properties: {str(e)}")
