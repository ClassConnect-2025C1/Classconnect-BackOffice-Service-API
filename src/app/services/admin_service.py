from src.app.repositories.admin_repository import AdminRepository
from src.app.exceptions.exceptions import (
    AdminNotFoundError,
    AdminAlreadyExistsError,
    WrongPasswordError,
)
from src.app.security.security import hash_password, verify_password


class AdminService:
    def __init__(self, repository: AdminRepository) -> None:
        self.repository = repository

    async def create_admin(self, new_email: str, new_password: str, creator_id: str):
        await self.assertAdminIDExist(creator_id)
        await self.assertAdminEmailNotExist(new_email)
        password_hashed = hash_password(new_password)
        return await self.repository.create(new_email, password_hashed, creator_id)
        # return await self.repository.create(new_email, new_password, creator_id)

    async def login_admin(self, email: str, password: str):
        admin = await self.repository.get_by_email(email)
        if not admin:
            raise AdminNotFoundError(email)
        await self.assertCorrectPassword(email, password, admin)
        return admin

    async def assertCorrectPassword(self, email, password, admin):
        if not verify_password(password, admin.hashed_password):
            # if not password == admin.hashed_password:
            raise WrongPasswordError(email)

    async def assertAdminEmailNotExist(self, email):
        if await self.repository.get_by_email(email):
            raise AdminAlreadyExistsError(email)

    async def assertAdminIDExist(self, other_id):
        if not await self.repository.get_by_id(other_id):
            raise AdminNotFoundError(other_id)
