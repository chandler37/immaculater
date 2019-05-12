from datetime import datetime


def jwt_payload_handler(user):
    from jwt_auth import settings
    return {
        'user_id': user.pk,  # DLC why not basically reimplement sessions? don't
                             # you need a blacklist of jwts otherwise for
                             # password changes, account deletions by user, or
                             # administrative disabling of accounts? Why not
                             # have a jwt_sessions table with a 64-bit
                             # pseudorandom number and just put that number
                             # here?
        'exp': datetime.utcnow() + settings.JWT_EXPIRATION_DELTA
    }
