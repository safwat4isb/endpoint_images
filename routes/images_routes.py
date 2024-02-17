from fastapi import APIRouter, UploadFile, File,HTTPException
from models import ImageData ,Imagebase64
from database.ravendb import store
from services.image_service import calculate_image_dimensions, save_image_data
import base64

router = APIRouter()

@router.post("/upload/", response_model=ImageData)
async def upload_image(file: UploadFile = File(...)):
    # Check if the uploaded file is an image
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Uploaded file is not an image.")

    # Read the image file content
    image_bytes = await file.read()

    # Calculate the width and height of the image
    width, height = calculate_image_dimensions(image_bytes)
    

    # Create an ImageProperties object with the necessary data
    image_properties = ImageData(
        image_path=file.filename,
        width=width,
        height=height
    )

    # Save the image data
    save_image_data(image_properties)

    # Return the image properties as the response
    return image_properties

@router.post("/process-image/")
async def process_image(image_data: Imagebase64):
    try:
        image_bytes = base64.b64decode(image_data.base64_string)
        width, height = calculate_image_dimensions(image_bytes)
       

        # Return the processed image as base64
        return {
            "width": width,
            "height": height,
            "base64_image":image_data.base64_string
           
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error processing image: {str(e)}")

@router.get("/image_properties/{image_id}", response_model=ImageData)
async def get_image_properties(image_id: str):
    try:
        full_document_id = f"ImageDatas/{image_id}"
        with store.open_session() as session:
            # Load the document by its ID
            result = session.load(full_document_id)
            
            # Check if the document exists
            if result is not None:
                # Extract image properties
                image_path = result.get("image_path")
                width = result.get("width")
                height = result.get("height")

                # Return image properties
                return ImageData(image_path=image_path, width=width, height=height)
            else:
                # If the document doesn't exist, raise HTTPException with status code 404
                raise HTTPException(status_code=404, detail="Image not found")
    except Exception as e:
        # If any error occurs during the process, raise HTTPException with status code 400
        raise HTTPException(status_code=400, detail=f"Error retrieving image properties: {str(e)}")