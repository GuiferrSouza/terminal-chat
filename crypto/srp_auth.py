from srptools import SRPContext, SRPClientSession, SRPServerSession
import os

def create_server(password: str):
    salt = os.urandom(16)
    ctx = SRPContext("user", password, salt=salt)
    verifier = ctx.get_verifier()
    return salt, verifier

def server_session(verifier, salt, A):
    ctx = SRPContext("user", None, salt=salt)
    server = SRPServerSession(ctx, verifier)
    B = server.public
    server.process(A)
    return server, B

def client_session(username, password, salt):
    ctx = SRPContext(username, password, salt=salt)
    client = SRPClientSession(ctx)
    return client