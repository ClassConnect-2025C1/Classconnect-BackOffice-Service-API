from src.app.db.db_client import get_db
from src.app.repositories.admin_repository import AdminRepository
from src.app.repositories.logs_repository import LogRepository
from src.app.services.admin_service import AdminService
from src.app.services.iam_service import IAMService

from fastapi import APIRouter, Depends, HTTPException
from src.app.security.security import oauth2_scheme, create_access_token, decode_token
from src.app.schemas.admin_schemas import (
    RegisterRequest,
    LoginRequest,
    TokenResponse,
    BlockUserRequest,
    ChangeRoleRequest,
)

from src.app.exceptions.exceptions import (
    AdminNotFoundError,
    AdminAlreadyExistsError,
    GetDataFromTokenError,
    WrongPasswordError,
    UserNotFoundError,
    BadRequestError,
)


def get_admin_service(db=Depends(get_db)) -> AdminService:
    repository = AdminRepository(db)
    service = AdminService(repository)
    return service


def get_iam_service(db=Depends(get_db)) -> IAMService:
    repository = LogRepository(db)
    service = IAMService(repository)
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


@router.patch("/block/{user_id}")
async def block_user(
    user_id: str,
    body: BlockUserRequest,
    token: str = Depends(oauth2_scheme),
    service: IAMService = Depends(get_iam_service),
):
    try:
        user = decode_token(token)
        await service.block_user(user_id, body.to_block)
        return {"message": "User blocked" if body else "User unblocked"}
    except GetDataFromTokenError:
        raise HTTPException(status_code=400, detail="Error getting data from token")
    except UserNotFoundError as e:
        raise HTTPException(
            status_code=404, detail=f"User with id '{user_id}' not found."
        )
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"An unexpected error occurred: {str(e)}"
        )


@router.patch("/change_role/{user_id}")
async def change_user_role(
    user_id: str,
    body: ChangeRoleRequest,
    token: str = Depends(oauth2_scheme),
    service: IAMService = Depends(get_iam_service),
):
    try:
        user = decode_token(token)
        await service.change_role(user_id, body.rol)
        return {"message": "User role changed" if body else "User role reverted"}
    except GetDataFromTokenError:
        raise HTTPException(status_code=400, detail="Error getting data from token")
    except UserNotFoundError as e:
        raise HTTPException(
            status_code=404, detail=f"User with id '{user_id}' not found."
        )
    except BadRequestError:
        raise HTTPException(
            status_code=400,
            detail="Invalid role provided. Possible roles are 'student' or 'teacher'.",
        )
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"An unexpected error occurred: {str(e)}"
        )
