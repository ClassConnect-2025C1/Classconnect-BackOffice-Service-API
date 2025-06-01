class AdminNotFoundError(Exception):
    def __init__(self, creator_id: str):
        self.creator_id = creator_id
        super().__init__(f"Creator with id '{creator_id}' not found.")
