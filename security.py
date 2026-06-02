import bcrypt

def gerar_hash(senha: str) -> str:
    senha_bytes = senha.encode("utf-8")
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(senha_bytes, salt).decode("utf-8")

def verificar_senha(senha: str, hash_salvo: str) -> bool:
    return bcrypt.checkpw(senha.encode("utf-8"), hash_salvo.encode("utf-8"))