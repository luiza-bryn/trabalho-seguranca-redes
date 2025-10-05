import time
import hmac
import hashlib
import json
import base64
import secrets
from typing import Optional
from servidor import Server
from Crypto.Cipher import AES
from Crypto.Protocol.KDF import PBKDF2
from Crypto.Random import get_random_bytes
from Crypto.Hash import SHA256

class Client:
    def __init__(self, server: Server):
        self.server = server
        self.username = None
        self.totp_secret = None
        self.salt = None
        self.logado = False
        with open("source/users.json", "r", encoding="utf-8") as f:
            self.salts = json.load(f)

    def _new_salt(self, nbytes=16):
        return secrets.token_bytes(nbytes)

    def _save_user(self, user):
        with open("source/users.json", "w", encoding="utf-8") as f:
            json.dump(user, f, indent=2)
        with open("source/users.json", "r", encoding="utf-8") as f:
            self.salts = json.load(f)

    def _derive_key(self, password: bytes, salt: bytes, iterations=200_000, dklen=32):
        return PBKDF2(password, salt, dkLen=dklen, count=iterations, hmac_hash_module=SHA256)
    
    def _pbkdf2(self, password: str, salt: bytes, iterations=1000) -> bytes:
        return hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, iterations, dklen=32)

    def _encrypt_file_aes_gcm(self, key, input_path: str):
        cipher = AES.new(key, AES.MODE_GCM)
        nonce = cipher.nonce

        with open(input_path, "rb") as f:
            texto_plano = f.read()
        texto_cifrado, tag = cipher.encrypt_and_digest(texto_plano)

        return nonce, tag, texto_cifrado

    def _decrypt_aes_gcm(self, key, nonce, tag, texto_cifrado):
        cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
        plaintext = cipher.decrypt_and_verify(texto_cifrado, tag)

        return plaintext

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
        self._save_user(user)
        
        key_dv = self._pbkdf2(password, self.salt)

        resp = self.server.register(username, key_dv)
        if resp.get("ok"):
            self.username = username
        else:
            print("Erro:", resp.get("error"))
        return resp

    def login(self, username: str, password: str) -> bool:
        # Verifica se usuário existe localmente e resgata salt
        with open("source/users.json", "r", encoding="utf-8") as f:
            self.salts = json.load(f)
        if username not in self.salts:
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
            self.logado = True
        return password_ok, totp_ok

    def enviar_arquivo(self, filepath: str) -> bool:
        try:
            # cifrar conteudo do arquivo antes de enviar
            username_bytes = self.username.encode('utf-8')
            chave_simetrica = self._derive_key(password=username_bytes, salt=self.salt)
            # cifrar conteudo com a chave
            nonce, tag, conteudo = self._encrypt_file_aes_gcm(chave_simetrica, filepath)
            # enviar para o servidor
            self.server.receber_arquivo(self.username, nonce, conteudo, tag, filepath.split("/")[-1])
            return True
        except Exception as e:
            print(f"Erro ao enviar arquivo: {e}")
            return False
    
    def listar_arquivos(self) -> Optional[list]:
        try:
            arquivos = self.server.listar_arquivos(self.username)
            return arquivos
        except Exception as e:
            print(f"Erro ao listar arquivos: {e}")
            return None
    
    def baixar_arquivo(self, filename: str) -> bool:
        try:
            conteudo_cifrado, nonce, tag = self.server.enviar_arquivo(self.username, filename)
            with open(f"source/arquivos_locais/{filename}", "wb") as f_out:
                f_out.write(nonce)
                f_out.write(tag)
                f_out.write(conteudo_cifrado)
            return True
        except Exception as e:
            print(f"Erro ao baixar arquivo: {e}")
            return False
    
    def decifrar_documento(self, file: str) -> bool:
        try:
            username_bytes = self.username.encode('utf-8')
            chave_simetrica = self._derive_key(password=username_bytes, salt=self.salt)
            with open(f"source/arquivos_locais/{file}", "rb") as f_in:
                nonce = f_in.read(16)
                tag = f_in.read(16) 
                conteudo_cifrado = f_in.read()
            conteudo = self._decrypt_aes_gcm(chave_simetrica, nonce, tag, conteudo_cifrado)
            with open(f"source/arquivos_locais_decifrados/decifrado_{file}", "wb") as f_out:
                f_out.write(conteudo)
            return True
        except Exception as e:
            print(f"Erro ao decifrar arquivo: {e}")
            return False
