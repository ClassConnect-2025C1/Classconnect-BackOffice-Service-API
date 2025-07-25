class AdminNotFoundError(Exception):
    def __init__(self, creator_id: str):
        self.creator_id = creator_id
        super().__init__(f"Admin identified by '{creator_id}' not found.")


class AdminAlreadyExistsError(Exception):
    def __init__(self, email: str):
        self.email = email
        super().__init__(f"Admin with email '{email}' already exists.")


class WrongPasswordError(Exception):
    def __init__(self, email: str):
        self.email = email
        super().__init__(f"Wrong password for admin with email '{email}'.")


class GetDataFromTokenError(Exception):
    def __init__(self):
        super().__init__(f"Error getting data from token")


class UserNotFoundError(Exception):
    def __init__(self, user_id: str):
        self.user_id = user_id
        super().__init__(f"User with ID '{user_id}' not found.")


class BadRequestError(Exception):
    def __init__(self):
        super().__init__(f"Bad request")
