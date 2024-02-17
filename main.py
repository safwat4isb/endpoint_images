from fastapi import FastAPI
from routes import uuid_routes,images_routes

app = FastAPI()


# Include route handlers
app.include_router(images_routes.router)
app.include_router(uuid_routes.router)