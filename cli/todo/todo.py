# -*- coding: utf-8 -*-

"""todo: A command-line interface to Immaculater.

You must set one command-line flag to use this:

> $0 --url=https://localhost:5000/todo/api

where $0 is however you invoke this script, perhaps 'python todo.py' or
/usr/local/bin/todo depending on whether or not you ran `python setup.py install`.

Optionally set the following to avoid username/password prompts:

-u username:password

In --read_only mode, writes are permitted but will not be saved to the database.
For example:

> $0 --ro "mkdir '/will not be there later'" ls
--project-- uid=1 --incomplete-- ---active--- inbox
--folder--- uid=13 'will not be there later'
> $0 --ro ls
--project-- uid=1 --incomplete-- ---active--- inbox

Using https, the password is not sent in the clear. Using http, it is. So
don't use http except with localhost, 127.0.0.1, or 0.0.0.0.

Every argument given is its own little command line, so quote appropriately:

> $0 "view needing_review" "echo lsprj:" lsprj "echo inctx @home:" "inctx @home"

That's not true when in --single_command (-s) mode:

> $0 -s -- ls -R "/my project"

It's best practice to use "--" to prevent todo.py from parsing the following
arguments as its own command-line flags.

If you don't give any arguments, an interactive read-eval-print loop runs.

To summarize, imagine creating a bash alias like so:

> alias todo="$0 --url=https://localhost:5000/todo/api -u foo:password"

We could now do the following:

> todo -v actionable -c /inbox "mkact 'buy almond milk'" "mkact 'buy soymilk'" "complete 'buy soymilk'" ls
--action--- uid=13 --incomplete-- 'buy almond milk' --in-context-- 'Actions Without Context'

Imagine another alias for quickly capturing a thought:
> alias notetoself="todo --cd /inbox -s -- mkact --allow_slashes"
> notetoself "buy cashew yogurt @the store"

Though you might prefer the following (see `help do`):
> alias notetoself="todo -s -- do"
> notetoself buy bicycle helmet

For help on Immaculater commands, run `$0 help` or `$0 help mkact` etc.
"""

__version__ = "0.1.4"

# TODO(chandler): Support && like the Django CLI does

import getpass
import os
import pipes
import shlex
import sys

import requests

import gflags as flags  # https://github.com/google/python-gflags

flags.DEFINE_string('encoding',
                    'utf-8',
                    'Output Unicode encoding')
flags.DEFINE_string('url',
                    'http://127.0.0.1:5000/todo/api',
                    'URL to POST to',
                    short_name='i')
flags.DEFINE_bool('verbose',
                  True,
                  'Be wordy.')
flags.DEFINE_bool('ro',
                  False,
                  'Read-only mode: Executes in a sandbox. Write operations are '
                  'permitted but will not be saved to the database.',
                  short_name='r')
flags.DEFINE_string('username_and_password',
                    None,
                    'Colon-separated username and password. If no colon is '
                    'present, this is the username and the password will be '
                    'prompted.',
                    short_name='u')
flags.DEFINE_bool('single_command',
                  False,
                  'Treats the command-line arguments as components of a single '
                  'Immaculater command. When using this you should probably '
                  'use "--" to mark all following command-line arguments as '
                  'positional arguments, not flags for this CLI.',
                  short_name='s')
flags.DEFINE_bool('version',
                  False,
                  'Prints version.')
flags.DEFINE_bool('help',
                  False,
                  'Prints help.')
flags.DEFINE_string('view',
                    'incomplete',
                    'View filter, e.g., "needing_review" or "all"',
                    short_name='v')
flags.DEFINE_string('cd',
                    None,
                    'Current working container, e.g., "/inbox"',
                    short_name='c')
flags.DEFINE_string('sort',
                    'alpha',
                    'Sorting algorithm for folders, projects, and contexts '
                    '(but not actions). E.g., "chrono" for chronological',
                    short_name='S')

FLAGS = flags.FLAGS


def _get_username_and_password():
  username, password = None, None
  if FLAGS.username_and_password:
    if ':' in FLAGS.username_and_password:
      username, password = FLAGS.username_and_password.split(':', 1)
    else:
      username = FLAGS.username_and_password
  if not username:
    username = getpass.getpass('Username: ')
    if not username:
      print('Username must be typed in or provided via --username_and_password')
      sys.exit(3)
  if not password:
    password = getpass.getpass('Password: ')
    if not username:
      print('Password must be typed in or provided via --username_and_password')
      sys.exit(3)
  return username, password


def _print(s):
  print(s.encode(FLAGS.encoding))


def _handle_commands(commands,
                     username=None,
                     password=None):
  commands = list(commands)
  if len(commands) != 1 or not commands[0].startswith('help'):
    if FLAGS.view:
      commands.insert(0, "view %s" % pipes.quote(FLAGS.view))
    if FLAGS.cd:
      commands.insert(0, "cd %s" % pipes.quote(FLAGS.cd))
    if FLAGS.sort:
      commands.insert(0, "sort %s" % pipes.quote(FLAGS.sort))
  headers = {'Content-type': 'application/json'}
  r = requests.post(FLAGS.url,
                    json={'commands': commands,
                          'read_only': FLAGS.ro},
                    headers=headers,
                    auth=(username, password))
  if r.status_code == 200:
    for x in r.json()['printed']:
      _print(x)
    return 0
  else:
    try:
      j = r.json()
      if isinstance(j, dict) and 'immaculater_error' in j:
        _print(j['immaculater_error'])
      else:
        _print(unicode(r.json()))
    except ValueError:
      _print('ERROR: Status code %s' % r.status_code)
      _print(r.text)
    return 1


def _repl(username=None, password=None):
  def print_store_message():
    if FLAGS.verbose:
      _print('*storing command to be sent to the server only with the next command*')

  def print_error(cmd):
    _print("*error* wrong number of arguments to %s; please 'quote your strings'" % cmd)

  def intercept_state_command(splits, cmd, default):
    if splits and splits[0] == cmd:
      if len(splits) > 2:
        print_error(cmd)
        return True, default
      if len(splits) > 1:
        print_store_message()
        return True, splits[1]
    return False, default

  while True:
    try:
      command = raw_input("!read-only sandbox!> " if FLAGS.ro else "> ")
    except EOFError:
      sys.exit(0)
    if command.lower() in ('exit', 'quit', 'bye', '\q'):
      sys.exit(0)
    splits = shlex.split(command)
    cmd = 'cd'
    if splits and splits[0] == cmd:
      if len(splits) > 2:
        print_error(cmd)
        continue
      if len(splits) > 1:
        FLAGS.cd = splits[1]
        print_store_message()
        continue
    should_continue, FLAGS.cd = intercept_state_command(splits, 'cd', FLAGS.cd)
    if should_continue:
      continue
    should_continue, FLAGS.view = intercept_state_command(splits, 'view', FLAGS.view)
    if should_continue:
      continue
    should_continue, FLAGS.sort = intercept_state_command(splits, 'sort', FLAGS.sort)
    if should_continue:
      continue
    return_value = _handle_commands(
      [command],
      username=username,
      password=password)
    if return_value != 0:
      _print("*error*")


def main():
  args = FLAGS(sys.argv)[1:]
  if FLAGS.version:
    print('Immaculater CLI Version %s' % __version__)
    sys.exit(0)
  if FLAGS.help:
    doc = sys.modules[_get_username_and_password.__module__].__doc__
    help_msg = flags.DocToHelp(doc.replace('%s', sys.argv[0]))
    _print(flags.TextWrap(help_msg, flags.GetHelpWidth()))
    _print('\n')
    _print(FLAGS.GetHelp())
    sys.exit(0)
  username, password = _get_username_and_password()
  if not args:
    _repl(username=username, password=password)
    sys.exit(0)
  if FLAGS.single_command:
    args = [u' '.join(pipes.quote(x) for x in args)]
  sys.exit(_handle_commands(args, username=username, password=password))
