# auth_sim.py
import os
import json
import base64
import secrets
import hashlib
import pyotp
from typing import Optional
from client import Client
from servidor import Server

# Demo rápido
if __name__ == "__main__":
    srv = Server()
    cli = Client(srv)

    # Registrar
    cli.register("alice", "SenhaForte123!")

    # Simular login
    result_password, result_totp = cli.login("alice", "SenhaForte123!")
    if result_password and result_totp:
        print("Login bem-sucedido!")
    else:
        print("Falha no login.")
        if not result_password:
            print("Senha incorreta.")
        if not result_totp:
            print("Código TOTP incorreto.")