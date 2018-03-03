[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

# The Command-Line Interface to Immaculater.

This is a standalone [Python](https://www.python.org/) command-line interface
using [Immaculater's](https://github.com/chandler37/immaculater) secure HTTP
API.

Read the first part of `./todo/todo.py` to understand if this is for you.

## Immaculater

Immaculater is a to-do list inspired by David Allen's book _Getting Things
Done_. It has Next Actions, Projects, Contexts and support for Reviews. It has
a command-line interface built into the website and this command-line
interface. It has a snappy, lightweight web UI that's usable on your phone as
well as your desktop.

For an Immaculater account, e-mail immaculaterhelp@gmail.com.

## Installation

Installation differs for users and developers.

### Recommended Installation

Unless you're a developer, use the following recipe:

- `python2 setup.py install` or, if python2 is not found, `python setup.py install`
- Look for a line like `Installing todo script` to find the path where the
  script is installed. On OS X using [Homebrew](https://brew.sh/) (recommended on
  OS X to get the latest version of python 2.7) it might be
  `/usr/local/bin/todo`.
- Run `todo --help` to get started.

### Power User Installation

If you don't want to alter your system's `/usr` directory, or you get
permissions errors when you try and don't want to use `sudo`, you may install
in a [virtualenv](https://virtualenv.pypa.io/en/stable/) as follows:

- `virtualenv -p python2 venv` or, if python2 from Homebrew is not found, `virtualenv venv`
- `source venv/bin/activate`
- `python setup.py install`
- `deactivate`
- `./venv/bin/todo --help`

You should not have to `source venv/bin/activate` each time you use it.

### Developer Installation

You may skip using `setup.py` and install and run this tool as follows:

- `virtualenv venv`
- `source venv/bin/activate`
- `pip install -r requirements.txt`
- `./todo-runner.py --help`


## Example Session

- `todo "do clean the garage @home"`
- `todo "mkprj /housekeeping"`
- `todo "mv '/inbox/clean the garage @home' /housekeeping"`
- `todo "ls /housekeeping"`

> `--action--- uid=13 --incomplete-- 'clean the garage @home' --in-context-- @home`

- `todo "inctx @home"`

> `--action--- uid=13 --incomplete-- 'clean the garage @home'`

- `todo "complete '/housekeeping/clean the garage @home'"`
- `todo "ls /housekeeping"`
- `todo "inctx @home"`
- `todo -v all "ls /housekeeping"`

> `--action--- uid=13 ---COMPLETE--- 'clean the garage @home' --in-context-- @home`

## How it Works

Using SSL for security and privacy, this tool reaches out to Immaculater's
Django UI's `/todo/api` HTTPS endpoint. That endpoint is not a REST API, just
an API that understand url-encoded forms and JSON.

If you provide a `http://` URL instead of an `https://` URL, your username and
password will be sent in the clear for anyone to see. The HTTP header is
base64-encoded, but that is not the same thing as encryption. Don't use
`http://`unless you're a developer using a throwaway account on a server on
your own machine.

## Help

E-mail immaculaterhelp@gmail.com if you have any problems.

## Source Code

See <https://github.com/chandler37/immaculater/blob/master/cli/>.

## Docker

- `docker build -t immaculater-cli .`
- `docker run -it immaculater-cli python2 todo-runner.py --help`

## Copyright

Copyright 2017 David L. Chandler

See the LICENSE file in this directory.

## Getting Things Done®

Immaculater is not affiliated with, approved or endorsed by David Allen or the
David Allen Company. David Allen is the creator of the Getting Things Done®
system. GTD® and Getting Things Done® are registered trademarks of the David
Allen Company. For more information on that company and its products, visit
GettingThingsDone.com
