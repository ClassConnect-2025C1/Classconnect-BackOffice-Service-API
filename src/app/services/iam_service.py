from src.app.externals.auth_external import block_user_auth, change_rol_auth
from src.app.repositories.logs_repository import LogRepository
from src.app.exceptions.exceptions import BadRequestError


class IAMService:
    def __init__(self, repository: LogRepository) -> None:
        self.repository = repository

    async def block_user(self, user_id: str, to_block: bool):
        await block_user_auth(user_id, to_block)
        return await self.repository.create_log(
            user_id, "block" if to_block else "unblock"
        )

    async def change_role(self, user_id: str, rol: str):
        await self.assertIsAPossibleRole(rol)
        await change_rol_auth(user_id, rol)
        return await self.repository.create_log(user_id, rol)

    async def assertIsAPossibleRole(self, role: str):
        possible_roles = ["student", "teacher"]
        if role not in possible_roles:
            raise BadRequestError()
