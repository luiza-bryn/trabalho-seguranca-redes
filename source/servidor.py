import hmac
import json
import base64
import secrets
import hashlib
import time
from typing import Optional


class Server:
    def __init__(self):
        with open("source/users.json", "r", encoding="utf-8") as f:
            self.users = json.load(f)

    def _new_salt(self, nbytes=16):
        return secrets.token_bytes(nbytes)

    def _scrypt_hash(self, password: str, salt: bytes) -> bytes:
        """"
        n: número de iterações precisa ser potência de 2
        r: tamanho de bloco
        p: paralelismo
        dklen: tamanho da chave derivada resultante
        """
        return hashlib.scrypt(password,
                              salt=salt,
                              n=2**14, r=8, p=1, dklen=64)

    def _totp_like_internal(self, key, digits: int = 6) -> str:
        """
        Gera um token dinâmico baseado em:
        - senha do usuário
        - tempo atual (arredondado para timestep)
        
        Retorna um código numérico de 'digits' dígitos.
        """
        # contador de tempo
        t = int(time.time() // 30)
        
        counter = t.to_bytes(8, 'big')
        
        # usar HMAC-SHA1 (sem segredo extra, só a senha)
        hmac_hash = hmac.new(key, counter, hashlib.sha1).digest()
        
        # truncamento dinâmico (RFC4226 style)
        offset = hmac_hash[-1] & 0x0F
        code_int = (int.from_bytes(hmac_hash[offset:offset+4], 'big') & 0x7FFFFFFF)
        
        # reduzir para o número de dígitos desejado
        code = str(code_int % (10 ** digits)).zfill(digits)
        return code
    
    def register(self, username: str, password: str) -> dict:
        if username in self.users:
            return {"ok": False, "error": "Usuário já existe"}
        with open("source/users.json", "r", encoding="utf-8") as f:
            self.users = json.load(f)

        salt_scrypt = self._new_salt(16)

        pwd_hash = self._scrypt_hash(password, salt_scrypt)

        self.users[username] = {
            "salt_scrypt": base64.b64encode(salt_scrypt).decode('utf-8'),
            "password_hash": base64.b64encode(pwd_hash).decode('utf-8')
        }

        with open("source/users.json", "w") as f:
            json.dump(self.users, f, indent=2)

        return {"ok": True}

    def verify_password(self, username: str, password) -> bool:
        record = self.users.get(username)
        print(record)
        print(record["salt_scrypt"])
        if not record:
            return False
        salt_scrypt = base64.b64decode(record["salt_scrypt"])
        expected = base64.b64decode(record["password_hash"])
        candidate = self._scrypt_hash(password, salt_scrypt)
        
        return secrets.compare_digest(candidate, expected)

    def verify_totp(self, key, totp_expected) -> bool:
        totp = self._totp_like_internal(key)
        if totp != totp_expected:
            return False
        return True