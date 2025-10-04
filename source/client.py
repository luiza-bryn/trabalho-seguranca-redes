import time
import hmac
import hashlib
import json
import base64
import secrets
from typing import Optional
from servidor import Server


class Client:
    def __init__(self, server: Server):
        self.server = server
        self.username = None
        self.totp_secret = None
        self.salt = None
        with open("source/local.json", "r", encoding="utf-8") as f:
            self.salts = json.load(f)

    def _new_salt(self, nbytes=16):
        return secrets.token_bytes(nbytes)

    def save_user(self, user):
        with open("source/local.json", "w", encoding="utf-8") as f:
            json.dump(user, f, indent=2)

    def _pbkdf2(self, password: str, salt: bytes, iterations=1000) -> bytes:
        return hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, iterations, dklen=20)

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

    def register(self, username: str, password: str):
        if username in self.salts:
            print("Usuário já existe localmente.")
            return True
        
        self.salt = self._new_salt(16)
        
        # Armazena salt localmente 
        user = {username: {
            "salt_pbkdf2": base64.b64encode(self.salt).decode('utf-8')
        }}
        self.save_user(user)
        
        key_dv = self._pbkdf2(password, self.salt)

        resp = self.server.register(username, key_dv)
        if resp.get("ok"):
            self.username = username
        else:
            print("Erro:", resp.get("error"))

    def login(self, username: str, password: str) -> bool:
        # Verifica se usuário existe localmente e resgata salt
        with open("source/local.json", "r", encoding="utf-8") as f:
            self.salts = json.load(f)
        if username not in self.salts:
            print("Usuário não encontrado localmente.")
            return False, False
        else:
            self.salt = base64.b64decode(self.salts[username]["salt_pbkdf2"])
        key_dv = self._pbkdf2(password, self.salt)
        totp = self._totp_like_internal(key_dv)
        password_ok = False
        totp_ok = False
        #Verifica senha
        if self.server.verify_password(username, key_dv):
            password_ok = True
        #Verifica TOTP
        if self.server.verify_totp(key_dv, totp):
            totp_ok = True
        if password_ok and totp_ok:
            self.username = username
        return password_ok, totp_ok

