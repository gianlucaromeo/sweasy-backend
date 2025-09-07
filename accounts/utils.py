import jwt, secrets, time
from django.conf import settings

EMAIL_VERIFY_TTL_SECONDS = 60 * 60 * 24  # 1 day

def generate_email_verification_token(user_id):
    now = int(time.time())
    payload = {
        "jti": secrets.token_urlsafe(22),
        "sub": str(user_id),
        "prp": "email_verify",
        "iat": now,
        "exp": now + EMAIL_VERIFY_TTL_SECONDS,
        "iat": now,
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")

def decode_and_validate_email_verification_token(token: str) -> dict:
    try:
        data = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.EMAIL_VERIFY_ALG],
            options={
                "require": ["jti", "sub", "prp", "iat", "exp"],
            },
        )
    except jwt.InvalidTokenError as e:
        print(e)
        raise jwt.InvalidTokenError(str(e))
    if data.get("prp") != "email_verify":
        raise jwt.InvalidTokenError("wrong purpose")
    return data
