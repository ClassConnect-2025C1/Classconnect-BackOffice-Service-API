from src.app.repositories.admin_repository import AdminRepository
from src.app.exceptions.exceptions import AdminNotFoundError, AdminAlreadyExistsError
from src.app.security.security import hash_password


class AdminService:
    def __init__(self, repository: AdminRepository) -> None:
        self.repository = repository

    async def create_admin(self, new_email: str, new_password: str, creator_id: str):
        self.assertAdminIDExist(creator_id)
        self.assertAdminEmailNotExist(new_email)
        password_hashed = hash_password(new_password)
        return await self.repository.create(new_email, password_hashed, creator_id)

    def assertAdminEmailNotExist(self, email):
        if self.repository.get_by_email(email):
            raise AdminAlreadyExistsError(email)

    def assertAdminIDExist(self, other_id):
        if not self.repository.get_by_id(other_id):
            raise AdminNotFoundError(other_id)
