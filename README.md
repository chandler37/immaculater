[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

# Immaculater

![Logo](immaculater/static/immaculater/immaculater_logo_small.png)

Immaculater is a simple to-do list, a website and a command-line interface
(CLI).

Immaculater is a Django project (a website) configured for use on Heroku (a
cloud hosting provider). It's a *P*ython implementation of *Y*et *A*nother
*T*o-*D*o *L*ist. Immaculater is the application; pyatdl (pronounced "PEE-ott")
is the Python library underneath it (see the `pyatdllib/` subdirectory).

Why yet another to-do list? This one is inspired by David Allen's book _Getting
Things Done_, so it has Next Actions, Projects, Contexts and support for
Reviews. It is open source. It has a command-line interface. It is meant to be
a literate program, a teaching tool. It has a snappy, lightweight web user
interface (UI) that's great on your phone as well as your desktop.

## Getting Help or an Immaculater Account

To get an Immaculater account, or for general help, e-mail
<immaculaterhelp@gmail.com>.

## I'm a User, not a Software Developer

There is a prominent "Help" page under the 'Other' drop-down on the top
navigation bar, and there is a
[40-minute screencast](https://youtu.be/DKrEw7zttKM).  If you
want to be a power user, try running `help` in the command-line interface on
the website (it's a prominent button on the home page). For a real command-line
interface that uses the same database as the website, see
[`cli/README.md`](https://github.com/chandler37/immaculater/blob/master/cli/README.md).

## I'm a Developer

The remainder of this document is for you. To get started, watch this
[screencast](https://youtu.be/xMsniAbH6Yk). Then watch
[this screencast on protocol buffers](https://youtu.be/zYSGmkwaB9A). There's
also a
[screencast on unguessable base64 URL slugs and django modeling of a nascent sharing feature](https://youtu.be/CsueX84gJw0). And
a
[screencast on a jquery-pjax tweak related to flash messages and the quick capture box on the home page](https://youtu.be/bZAf5GWgoW8). And
a [screencast coding up the "Delete Completed" feature](https://youtu.be/zQDLUs6IRGY).

Next, forget about Heroku
and Django and focus on the original command-line interface (as opposed to
`cli/todo.py` which requires the Django server). You'll find it in the
`pyatdllib` subdirectory -- see
[`pyatdllib/README.md`](https://github.com/chandler37/immaculater/blob/master/pyatdllib/README.md). You
will need to run `pip install -r requirements.txt ` inside a `virtualenv` (see
below) before `make test` will pass or the CLI will run. You can use `runme.sh`
to start the original CLI.

## One-time Installation

 - Use [Homebrew](https://brew.sh/) to install python2 and python3. Its python2
   will be more up to date than your mac's system python and will in other ways
   better match the version of python you'll use on heroku.
 - Create a virtualenv with `virtualenv -p python2 venv`
 - `source venv/bin/activate`
 - Install postgresql. On OS X, `brew install postgresql` after installing
   [Homebrew](https://brew.sh/). On Linux, `apt-get install postgresql postgresql-contrib`
 - On Linux, `apt-get Install python-dev python3-dev`
 - Run `pip install -r requirements.txt` (again, after activating the virtualenv)
 - Install the [Heroku CLI](https://devcenter.heroku.com/articles/heroku-cli)
 - Create a Heroku account
 - Run `heroku login`

## One-Time Local Server Setup

 - `python manage.py migrate`
 - `python manage.py createsuperuser`

## One-Time Heroku Setup

 - `heroku create -a <yourprj>`
 - Or, if you already created your project but you're working from a new
   `pyatdl` directory, run `heroku git:remote -a <yourprj>` and then run `git
   remote add` as directed.
 - Folow the steps below for 'Heroku Deployment'
 - Generate two encryption keys as follows:

> $ heroku run python manage.py shell

> Python 2.7.14 (default, Sep 26 2017, 13:42:32) 

> > from cryptography.fernet import Fernet

> > Fernet.generate_key()

> 'cLlDneYkn69ZePyWcU9_mltFy4MwYf5pyqUnP-M8PxE='

> > Fernet.generate_key()

> 'mVb2CBYEwFi4sc8B7jpeDiIesuk6L7k1d_DI0sLC7PU='

> > Fernet.generate_key()

> 'Orjuw_obnZGQIR96CUgDVqmvW0V3Ea3yq4uJon-RLT8='

 - `heroku config:set FERNET_PROTOBUF_KEY=cLlDneYkn69ZePyWcU9_mltFy4MwYf5pyqUnP-M8PxE=`
 - `heroku config:set FERNET_COOKIE_KEY=mVb2CBYEwFi4sc8B7jpeDiIesuk6L7k1d_DI0sLC7PU=`
 - `heroku config:set DJANGO_SECRET_KEY=Orjuw_obnZGQIR96CUgDVqmvW0V3Ea3yq4uJon-RLT8=`
 - `heroku run python manage.py createsuperuser`
 - Log into https://<yourprj>.herokuapp.com/
 - Go to https://<yourprj>.herokuapp.com/admin to create additional user
   accounts
 - Consider signing up for https://papertrailapp.com/ e.g. to see your HTTP
   500s' stack traces

## Heroku Deployment

 - `git checkout master`
 - `git pull`
 - `git push heroku master`
 - See below about `heroku run python manage.py migrate`, necessary
   only rarely when the database schema changes

## Database migrations

 - Edit the models.
 - `python manage.py makemigrations todo`
 - Test locally with `python manage.py migrate`
 - `git checkout master`
 - `git pull`
 - `git checkout -b migration_branch`
 - `git add <new file>`
 - `git commit`
 - `git push origin migration_branch`
 - Make a pull request and get it merged
 - `git checkout master`
 - `git pull`
 - `git push heroku master`
 - `heroku run python manage.py migrate`

## Source Code and How to Commit

The source code lives at [https://github.com/chandler37/immaculater](https://github.com/chandler37/immaculater).

See above for the magical `git clone` incantation and git documentation.

Our practice is never to push directly to `master`. Instead, create a feature
branch and push to it (for details on the 'feature branch' idiom see
https://www.atlassian.com/git/tutorials/comparing-workflows/feature-branch-workflow/). You
can do a remote commit with the following:

 - `git checkout master`
 - `git pull`
 - `git checkout -b your_feature_branch_goes_here`
 - Make your edits
 - `source venv/bin/activate`
 - `(cd pyatdllib && make test)`
 - Test using `heroku local web` or `DJANGO_DEBUG=True python manage.py runserver 5000`
 - Navigate to [the local server](http://127.0.0.1:5000/) and log in
   as the superuser you created above under 'One-Time Local Server Setup'
 - `git status` to see any new files and confirm what branch you're on. If you
   see `pyatdllib/core/pyatdl_pb2.py` in the diff but you didn't edit
   `pyatdl.proto`, that's because of differences in the version of the
   [protocol buffer]((https://developers.google.com/protocol-buffers/))
   compiler. You can revert with `git checkout -- pyatdllib/core/pyatdl_pb2.py`
 - `git diff`
 - `git add X Y Z` for any new files X Y and Z
 - `git commit --all`
 - `git push origin your_feature_branch_goes_here`
 - Go to
    [the pull requests page at github](https://github.com/chandler37/immaculater/pulls)
    and choose 'New pull request' to create a request to merge your feature
    branch into `master`.
 - Now find a code reviewer and work with your reviewer towards consensus (making
    commits to your feature branch that the pull request will automagically
    incorporate after `git push origin your_feature_branch_goes_here`). When ready,
    just press the 'Merge' button and let the website do the actual change to
    `master`. You can then close the source branch on github and delete your
    local branch with
	`git checkout master && git pull && git branch -d your_feature_branch_goes_here`

When done with your feature, ensure all tests pass (`(cd pyatdllib && make
test)` and run pylint (`make pylint` after `pip install pylint` (inside an
activated virtualenv)).  The very best practice is to run `make cov` (first
`pip install coverage` (inside an activated virtualenv)) and ensure that your
change has optimal unittest code coverage. You get bonus points for installing
pychecker and running `make pychecker`.

The above practices give us the benefit of easy code reviews and ensure that
your buggy works in progress doesn't interfere with other developers. Try to
make your feature branch (and thus the code review) as short and sweet as you
can. E.g., if you had to refactor something as part of your change, create one
feature branch for the refactoring and another that builds on it.

## Command-Line Interface (CLI)

There are two CLIs, one which uses local files and one which uses secure HTTP
to DJango running atop Heroku. The former is in `pyatdllib/ui/immaculater.py`;
the latter is in `cli/todo.py`.

Oops, and there's a third -- it's built into the Django UI, the `/todo/cli` endpoint.

## Encryption

The to-do list is stored in a
[Fernet](https://cryptography.io/en/latest/fernet/)-encrypted field in the
database. The key is stored in a Heroku config variable. An attacker would have
to break into both places to read your data.

The Django server is set up to require the use of SSL (HTTPS) at all times.

## Security updates

You might want to subscribe to https://groups.google.com/forum/#!forum/django-allauth-announce

## History

This installation was built with the help of
https://github.com/heroku/heroku-django-template so see `README-heroku-django.md`.

You'll find here code from https://github.com/yiisoft/jquery-pjax,
a fork of defunkt's jquery-pjax.

You'll find here code from https://github.com/eventials/django-pjax.

You'll find here code from https://craig.is/killing/mice /
https://github.com/ccampbell/mousetrap

You'll find as dependencies the following:

- https://github.com/google/google-apputils
- https://github.com/sparksuite/simplemde-markdown-editor
- https://github.com/google/python-gflags
- https://github.com/abseil/abseil-py
- https://github.com/google/protobuf

## Future Directions -- Help Wanted

grep the code for TODOs using `grepme.sh`.

Wouldn't it be nice if we had the following:

- A login page that doesn't change style upon an invalid login
- [Docker support](https://docs.docker.com/compose/django/)
- Voice integration with Alexa, Siri, Google Home, etc.
- A better web app than the one found here, something slick
  like the 'mail.google.com' interface to GMail
- Expanding the setup.py magic built around cli/todo.py into a proper PyPI
  package listed publicly
- An iOS app
- An Android app
    - Perhaps SL4A scripting layer for android
    - See kivy.org which uses python-for-android under the hood, particularly the
      'notes' tutorial app.
        - Dependence: Cython-0.22
        - Beware of https://www.bountysource.com/issues/7397452-cython-0-22-does-not-compile-master
            - Workaround: Replace 'except *' with ''
        - `~/git/kivy/examples/tutorials/notes/final$ buildozer -v android debug`
        - `~/git/kivy/examples/tutorials/notes/final$ buildozer -v android debug deploy run`
- An actual filesystem (remember how Plan 9 made pretty much everything pretend
  to be a filesystem? We already are pretending.) Starting with a linux
  filesystem (see FUSE) and an OS X filesystem (see [FUSE for macOS](https://osxfuse.github.io/))
- Per-user encryption. We already use [Fernet](https://cryptography.io/en/latest/fernet/)
  to encrypt the to-do list, but some users would prefer a
  second layer of encryption such that an attacker would have to break a
  user's password to see the user's data. Resetting passwords would erase
  all data.
- Login with Google/Facebook/Discord/etc. [Work in Progress on the allauth0 branch]

## Copyright

Copyright 2017 David L. Chandler

See the LICENSE file in this directory.

## Getting Things Done®

Immaculater is not affiliated with, approved or endorsed by David Allen or the
David Allen Company. David Allen is the creator of the Getting Things Done®
system. GTD® and Getting Things Done® are registered trademarks of the David
Allen Company. For more information on that company and its products, visit
GettingThingsDone.com
