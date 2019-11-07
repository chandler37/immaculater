"""Defines DataError, an exception."""


class Error(Exception):
  pass


class DataError(Error):
  """A cousin of ValueError -- the data passed break fundamental constraints."""
