from fastapi import Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from src.auth.firebase import verify_token

# HTTPBearer is FastAPI's built-in helper for reading Bearer tokens
# from the Authorization header. It handles the parsing — we just
# get the raw token string from credentials.credentials.
security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> str:
    """
    FastAPI dependency that extracts and verifies the Firebase ID token.
    Any route that uses Depends(get_current_user) is automatically
    protected — if the token is missing or invalid, FastAPI returns
    HTTP 401 before the route handler even runs.
    Returns the firebase_uid of the verified user.
    """
    return verify_token(credentials.credentials)