from datetime import datetime

def jwt_payload_handler(user):
    from jwt_auth import settings
    return {
        'user_id': user.pk,
        'exp': datetime.utcnow() + settings.JWT_EXPIRATION_DELTA
    }
