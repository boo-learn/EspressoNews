from fastapi import FastAPI

from admin_service.core.const import (
    OPEN_API_DESCRIPTION,
    OPEN_API_TITLE,
)
from admin_service.endpoints import (
    auth,
    users
    # movies,
)
from admin_service.version import __version__


app = FastAPI(
    title=OPEN_API_TITLE,
    description=OPEN_API_DESCRIPTION,
    version=__version__,
    swagger_ui_parameters={"defaultModelsExpandDepth": -1},
)

app.include_router(auth.router)
app.include_router(users.router)
