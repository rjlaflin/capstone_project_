import uuid


class LoginUtil:

    @staticmethod
    def generate_tmp_password() -> str:
        return str(uuid.uuid4())[:8]
