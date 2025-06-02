from src.app.db.db_client import get_db
from src.app.repositories.admin_repository import AdminRepository
from src.app.services.admin_service import AdminService

from fastapi import APIRouter, Depends, HTTPException
from src.app.security.security import oauth2_scheme, create_access_token, decode_token
from src.app.schemas.admin_schemas import RegisterRequest, LoginRequest, TokenResponse

from src.app.exceptions.exceptions import (
    AdminNotFoundError,
    AdminAlreadyExistsError,
    GetDataFromTokenError,
    WrongPasswordError,
)


def get_admin_service(db=Depends(get_db)) -> AdminService:
    repository = AdminRepository(db)
    service = AdminService(repository)
    return service


router = APIRouter(tags=["admin"])


@router.post("/register")
async def register_admin(
    data: RegisterRequest,
    token: str = Depends(oauth2_scheme),
    service: AdminService = Depends(get_admin_service),
):
    try:
        user = decode_token(token)
        await service.create_admin(
            new_email=data.email,
            new_password=data.password,
            creator_id=user.id,
        )
        return
    except AdminNotFoundError as e:
        raise HTTPException(
            status_code=401, detail=f"Creator with id '{e.creator_id}' not found."
        )
    except AdminAlreadyExistsError as e:
        raise HTTPException(
            status_code=400, detail=f"Admin with email '{e.email}' already exists."
        )
    except GetDataFromTokenError:
        raise HTTPException(status_code=400, detail="Error getting data from token")
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"An unexpected error occurred: {str(e)}"
        )


@router.post("/login", response_model=TokenResponse)
async def login_admin(
    body: LoginRequest,
    service: AdminService = Depends(get_admin_service),
):
    try:
        admin = await service.login_admin(body.email, body.password)
        token = create_access_token(id=admin.id, email=admin.email)
        return TokenResponse(access_token=token, token_type="bearer")
    except AdminNotFoundError as e:
        raise HTTPException(
            status_code=404, detail=f"Admin with email '{e.creator_id}' not found."
        )
    except WrongPasswordError as e:
        raise HTTPException(
            status_code=401, detail=f"Wrong password for admin with email '{e.email}'."
        )
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"An unexpected error occurred: {str(e)}"
        )
