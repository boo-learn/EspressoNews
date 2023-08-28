from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
)
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from admin_service.core.const import (
    AUTH_TAGS,
    AUTH_URL,
    TOKEN_TYPE
)
from admin_service.core.depends import get_db_session
from admin_service import schemas, models, repository

router = APIRouter(prefix="" + AUTH_URL, tags=AUTH_TAGS)


@router.post("/login/access-token", response_model=schemas.TokenSchema)
def login_access_token(
        session: Session = Depends(get_db_session),
        form_data: OAuth2PasswordRequestForm = Depends()
):
    """
    OAuth2 compatible token login, get an access token for future requests
    """
    user = crud.admin_user.authenticate(
        session, email=form_data.username, password=form_data.password
    )
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    # elif not crud.admin_user.is_active(user):
    #     raise HTTPException(status_code=400, detail="Inactive user")
    # access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return {
        "access_token": user.create_access_token(),
        "token_type": TOKEN_TYPE,
    }

# @router.post("/login/test-token", response_model=schemas.User)
# def test_token(current_user: models.AdminUser = Depends(deps.get_current_user)) -> Any:
#     """
#     Test access token
#     """
#     return current_user
