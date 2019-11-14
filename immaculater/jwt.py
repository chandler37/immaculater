from django.utils import timezone


def jwt_payload_handler(user):
  """JSON Web Token payload creator.

  Yes, we've reimplemented sessions. If we just use a User's primary key, don't we need a blacklist of JWTs?
  Otherwise, for password changes, account deletions by user, or administrative disabling of accounts, we'll still
  allow in the old JWT until it expires. Why not have a jwt_sessions table with a 64-bit pseudorandomly assigned number
  as primary key and just put that number here, base64-encoded to avoid the JSON disaster of treating integers greater
  than 2**53 in absolute value as numbers (see
  https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Number/MAX_SAFE_INTEGER)?

  You may argue that now we have to hit the database. We have to anyway in case the admin disabled the user. The story
  about "we must be planet-scale so we cannot contact the database or an auth server" is irrelevant for this and almost
  every application, and I think even if you need to be planet-scale you'd be foolish to put things like 'is this User
  a SuperUser?' inside a JWT because the cryptography can be broken and you want to limit the damage if it is.

  If you don't do the above, you have something else to do: TODO(chandler37): JWT payloads are unencrypted. Do not use
  the real user ID because it tells how fast the site is growing. Use a random 64-bit number from a new table
  user_random_id with columns (user.id, 64-bit number) and an index on each. This is better than encrypting the JWT, in
  my opinion, because that can be cracked.

  """
  from pyatdllib.ui import immaculater
  from todo import models
  from jwt_auth import settings as jwt_auth_settings
  slug = immaculater.Base64RandomSlug(64)
  expiry = timezone.now() + jwt_auth_settings.JWT_EXPIRATION_DELTA
  new_model = models.JwtSession(
    user=user,
    slug=slug,
    expires_at=expiry)
  new_model.save()
  return {"slug": slug, "expiry": expiry.strftime('%s')}
