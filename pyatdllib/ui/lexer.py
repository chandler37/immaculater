"""Routines that do lexical analysis.

E.g., this module helps parse commands like 'chctx Context0 Action0'.
"""

from __future__ import unicode_literals

import shlex

import gflags as flags  # https://code.google.com/p/python-gflags/


FLAGS = flags.FLAGS

flags.DEFINE_bool(
  'pyatdl_allow_command_line_comments', False,
  'Regarding parsing the command line (e.g., "mkctx \'At Home\'"), allow '
  'end-of-line comments like "ls -l # ctime"?')


class Error(Exception):
  """Base class for this module's exceptions."""


class UIDSyntaxError(Error):
  """Invalid UID syntax."""


class ShlexSyntaxError(Error):
  """Invalid syntax."""


def ParseSyntaxForUID(candidate):
  """Returns None unless a UID was successfully parsed.

  Otherwise returns a positive integer.

  Args:
    candidate: basestring
  Returns:
    None|int
  Raises:
    UIDSyntaxError
  """
  if candidate.lower().startswith('uid=') and candidate.count('=') == 1:
    (_, rhs) = candidate.split('=')
    try:
      an_integer = int(rhs, 10)
      if an_integer < -2**63 or an_integer >= 2**63 or an_integer == 0:
        raise ValueError('reraise')
      return an_integer
    except ValueError:
      raise UIDSyntaxError('Illegal "uid" syntax. Correct syntax: uid=N where '
                           '-2**63 <= N < 2**63 is a signed decimal integer that is not zero')
  return None


def SplitCommandLineIntoArgv(space_delimited_argv, posix=True):
  """Given a string, returns a vector of strings, argv.

  Don't set posix False. Quote characters are removed by POSIX (see unittest),
  and we therefore do not play well with non-POSIX.

  Args:
    space_delimited_argv: str
    posix: bool
  Raises:
    Error
  """
  try:
    return shlex.split(space_delimited_argv,
                       comments=FLAGS.pyatdl_allow_command_line_comments,
                       posix=posix)
  except ValueError as e:
    raise ShlexSyntaxError('Cannot parse command line. %s' % str(e))
