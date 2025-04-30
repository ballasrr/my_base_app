from typing import Annotated
from routers.items import router as items_router
from fastapi import Depends, FastAPI

app = FastAPI()

app.include_router(items_router, prefix='/items')
