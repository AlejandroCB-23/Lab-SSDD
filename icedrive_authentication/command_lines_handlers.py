import sys
from .app import AuthenticationApp
from .app import ClientApp

def server():
    """Handle the icedrive-authentication program."""
    app = AuthenticationApp()
    return app.main(sys.argv)

def client():
    """Handle the icedrive-authentication program."""
    app = ClientApp()
    return app.main(sys.argv)