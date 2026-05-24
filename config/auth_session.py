class AuthSession:
    _instance = None
    usuario_actual = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(AuthSession, cls).__new__(cls)
        return cls._instance

    @classmethod
    def set_usuario(cls, usuario):
        cls.usuario_actual = usuario

    @classmethod
    def get_usuario(cls):
        return cls.usuario_actual

    @classmethod
    def clear(cls):
        cls.usuario_actual = None
