[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

# Immaculater

![Logo](immaculater/static/immaculater/immaculater_logo_small.png)

Immaculater is a simple to-do list, a website and a command-line interface
(CLI).

Immaculater is a Django project (a website) configured for use on Heroku (a
cloud hosting provider). It's a *P*ython implementation of *Y*et *A*nother
*T*o-*D*o *L*ist. Immaculater is the application; pyatdl (pronounced "PEE-ott")
is the Python library underneath it (see the `pyatdllib/` subdirectory).

Thanks to <https://github.com/chandler37/immaculater_dart> there is now access
from Dart (the language used by Flutter iOS/Android/desktop/web apps).

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
[immaculater-cli](https://github.com/chandler37/immaculater-cli).

## I'm a Developer

The remainder of this document is for you. To get started, watch this
[screencast](https://youtu.be/xMsniAbH6Yk). Then watch
[this screencast on protocol buffers](https://youtu.be/zYSGmkwaB9A). There's
also a
[screencast on unguessable base64 URL slugs and django modeling of a nascent sharing feature](https://youtu.be/CsueX84gJw0). And
a
[screencast on a jquery-pjax tweak related to flash messages and the quick capture box on the home page](https://youtu.be/bZAf5GWgoW8). And
a [screencast coding up the "Delete Completed" feature](https://youtu.be/zQDLUs6IRGY).

Next, forget about Heroku and Django and focus on the original command-line
interface (as opposed to <https://github.com/chandler37/immaculater-cli> which
requires the Django server). You'll find it in the `pyatdllib` subdirectory --
see
[`pyatdllib/README.md`](https://github.com/chandler37/immaculater/blob/master/pyatdllib/README.md). You
will need to run `make pipinstall` inside an activated `virtualenv` (see below)
before `make test` will pass or the CLI will run. You can use `runme.sh` to
start the original CLI.

## Python 3

Immaculater and pyatdl require 3.6+ because DJango 2 and pyatdl require Python 3.

The file './runtime.txt' names a version of Python that is particularly well
tested because it's used in production (on Heroku).

## One-time Installation

 - If you're on MacOS, use [Homebrew](https://brew.sh/) to install python3. But
    you may run into problems with 3.7 or later and need to install 3.6 using the
    recipe at
    https://stackoverflow.com/questions/51125013/how-can-i-install-a-previous-version-of-python-3-in-macos-using-homebrew
 - On Linux, `apt-get Install python-dev python3-dev`
 - Install postgresql. On MacOS, `brew install postgresql` after installing
   [Homebrew](https://brew.sh/). On Linux, `apt-get install postgresql postgresql-contrib`
 - `pip3 install virtualenv`
 - Create a virtualenv with `make venv`
 - `source venv/bin/activate`
 - Notice how your command prompt mentions `(venv)` now to let you know that
   the virtualenv is activated. You can `deactivate` at any time or exit the
   shell to deactivate.
 - Run `make pipinstall` (again, after activating the virtualenv)
 - If the above fails on the `cryptography` package you may need to `export
 LDFLAGS=-L/usr/local/opt/openssl/lib` and `export LDFLAGS=-L/usr/local/opt/openssl/lib`
 - Install the [Heroku CLI](https://devcenter.heroku.com/articles/heroku-cli)
 - Create a Heroku account
 - Run `heroku login`

## One-Time Local Server Setup

 - `make localmigrate`
 - `make localsuperuser`
 - `sqlite3 db.sqlite3` helps you see the local database if you need to.

## One-Time Heroku Setup

 - `heroku create -a <yourprj>`
 - Or, if you already created your project but you're working from a new
   `immaculater` directory, run `heroku git:remote -a <yourprj>` and then run `git
   remote add` as directed.
 - Folow the steps below for 'Heroku Deployment'
 - Generate two encryption keys as follows:

> $ heroku run python manage.py shell

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
   500s' stack traces (use `heroku addons:open papertrail`)

## Heroku Deployment

 - `git checkout master`
 - `git pull`
 - `git push heroku master`
 - See below about `heroku run python manage.py migrate`, necessary
   only rarely when the database schema changes

If the push fails because of trouble with pip (e.g., `mount:
failure.bad-requirements: No such file or directory`), try clearing the build
cache:
 - `heroku plugins:install heroku-repo`
 - `heroku repo:purge_cache -a YOURAPPNAME`

(An advanced technique is to push a topic branch to Heroku, which requires
pushing it to what the `heroku` remote considers `master`. This will likely
require a force push later (`-f` forces) to push `master` back. You can do this
by (assuming `git status` shows you are on your topic branch) running `git push
-f heroku HEAD:master`.)

## Database Migrations

First you may want to do a manual backup of your database with `heroku
pg:backups:capture --app <YOUR APP NAME>`.

 - Edit the models.
 - `python manage.py makemigrations todo`
 - Test locally with `python manage.py migrate`
 - `git checkout master`
 - `git pull`
 - `git checkout origin/master -b migration_branch`
 - `git add <new file>`
 - `git commit`
 - `git push origin migration_branch`
 - Make a pull request and get it merged
 - `git checkout master`
 - `git pull`
 - `git push heroku master`
 - `heroku run python manage.py migrate`

You should not need to put your app in maintenance mode via `heroku
maintenance:on -a <YOUR APP NAME>` but if you are ignoring best practices and
mixing a database change with a code change, it's probably best.

If you want to poke around at the production postgresql database, do something like the following:

```
USEFUL:
/i$ heroku pg:psql
--> Connecting to postgresql-...
immaculater::DATABASE=> \dt
       List of relations
 Schema |                 Name                 | Type  |     Owner
--------+--------------------------------------+-------+----------------
 public | account_emailaddress                 | table | ...
immaculater::DATABASE=> select * from auth_user order by last_login desc;
...
immaculater::DATABASE=> select * from todo_todolist limit 1;
 user_id | contents |          created_at           |          updated_at           | encrypted_contents | encrypted_contents2
---------+----------+-------------------------------+-------------------------------+--------------------+---------------------
       1 | ........ | 2017-07-05 02:34:30.285521+00 | 2017-07-05 02:34:30.285538+00 |                    |
immaculater::DATABASE=> select pg_column_size(encrypted_contents2), octet_length(encrypted_contents2) from todo_todolist where user_id = 51919;
 pg_column_size | octet_length
----------------+--------------
     110540 |       110540
(1 row)
```

## Upgrading Third-Party Dependencies

The file `requirements.txt` pins third-party dependencies like `protobuf` and
`Django` to versions that are tested. If you wish to upgrade, change the
version. E.g., if you learn of a security vulnerability in `Django`, change its
version. Don't change any other libraries. Installation may fail if the new
`Djanjo` requires a newer version of something else. Upgrade that something
else.

If you wish to upgrade everything possible, run `make upgrade` which does the
following: Edit `requirements.txt` so that it no longer contains any version
information. You can do this via `sed -i "" -e "s/=.*//"
requirements.txt`. Then `source venv/bin/activate; pip3 install -r
requirements.txt`. (This is a subset of what `make pipinstall` does; we do not
wish to install test dependencies at this point.) You will fetch the latest of
everything. Now run `pip3 freeze > requirements.txt` to pin once more. Now run
`make pipinstall test`.

Understand each change by reading changelogs or studying the diff of the source
code. You don't want to push the latest-but-not-necessarily-greatest to
production accidentally, so make sure `requirements.txt` is frozen anew (which
`make upgrade` does for you).

The `protobuf` library is unique in that it contains Python a library used by
the compiled `pyatdl.proto` file but also contains the protocol buffer
compiler, `protoc`. You may wish to recompile
`pyatdllib/core/pyatdl_pb2.py`. `make clean` will remove it and `make test`
will trigger a new compilation. You might prefer to install `protoc` via
homebrew using `brew install protobuf` but it is not always up to date and is
perhaps not built with the same compiler options as the official releases at
https://github.com/protocolbuffers/protobuf/releases.

The real test is whether or not the new `pyatdl_pb2.py` can work with data
inside postgresql that was created by the old version. It's the whole point of
the library, but you should definitely run the old code to populate the
database and then run the new code and see if it works. An automated test of
this would be a welcome pull request.

Here's an example of studying changelogs and the differences in the source
code:

- First do a web search to find the changelog, if there is one. Read it. Then...
- `cd /tmp`
- `git clone https://github.com/protocolbuffers/protobuf.git`
- `cd protobuf`
- `git tag -l --sort=version:refname`
- `git diff v3.5.2..v3.7.0` # or whatever your old and new versions are
- Enjoy your 350000 line diff. You might want to restrict your investigations
  to the files with 'python' in the name, staring with
  'python/google/protobuf/'.

Why do this to yourself, though? Upgrading everything is not for the faint of
heart. Limit upgrades to security releases and you're less likely to suffer
data loss.

When deploying your change, first create a backup of the postgresql database.

If you need help understanding why things are installed, see
[https://pypi.org/project/pipdeptree/](pipdeptree). You must install it inside
the virtualenv (`make pipdeptree`).

And don't forget to test with the same python version you're using in
production, which itself must at times be upgraded by editing `runtime.txt`.

## Source Code and How to Commit

The source code lives at [https://github.com/chandler37/immaculater](https://github.com/chandler37/immaculater).

See above for the magical `git clone` incantation and git documentation.

Our practice is never to push directly to `master`. Instead, create a feature
branch and push to it (for details on the 'feature branch' idiom see
https://www.atlassian.com/git/tutorials/comparing-workflows/feature-branch-workflow/). You
can do a remote commit with the following:

 - `git checkout master`
 - `git pull`
 - `git checkout origin/master -b your_feature_branch_goes_here`
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
   compiler (we use version 3.5.1). You can revert with `git checkout -- pyatdllib/core/pyatdl_pb2.py`
 - `git diff`
 - `git add X Y Z` for any new files X Y and Z
 - `git commit --all`
 - `git push origin HEAD` which has a shortcut `make pushbranch`
 - Go to
    [the pull requests page at github](https://github.com/chandler37/immaculater/pulls)
    and choose 'New pull request' to create a request to merge your feature
    branch into `master`.
 - Now find a code reviewer and work with your reviewer towards consensus (making
    commits to your feature branch that the pull request will automagically
    incorporate after `git push origin HEAD`). When ready,
    just press the 'Merge' button and let the website do the actual change to
    `master`. You can then close the source branch on github and delete your
    local branch with
	`git checkout master && git pull && git branch -d your_feature_branch_goes_here`

When done with your feature, ensure all tests pass (`make test`) and run pylint
(`make pylint` after `pip3 install pylint` (inside an activated virtualenv))
and `flake8 .`.  The very best practice is to run `make cov` (first `pip3
install coverage` (inside an activated virtualenv)) and ensure that your change
has optimal unittest code coverage (this does not work for the tests run by
`run_django_tests.py`). You get bonus points for installing pychecker and
running `make pychecker`.

The above practices give us the benefit of easy code reviews and ensure that
your buggy works in progress doesn't interfere with other developers. Try to
make your feature branch (and thus the code review) as short and sweet as you
can. E.g., if you had to refactor something as part of your change, create one
feature branch for the refactoring and another that builds on it.

## Command-Line Interface (CLI)

There are two CLIs, one which uses local files and one which uses secure HTTP
to DJango running atop Heroku. The former is in `pyatdllib/ui/immaculater.py`;
the latter is in <https://github.com/chandler37/immaculater-cli>.

Oops, and there's a third -- it's built into the Django UI, the `/todo/cli` endpoint.

## Discord Bot

See <https://github.com/chandler37/immaculater-discord-bot> for a wrapper
around the CLI. You can go a long way with two CLI commands, 'todo' and
'do'. To use the Discord bot you must set `USE_ALLAUTH` to `True`; see
below. Users will have to sign in via Discord first on the Django website
before the bot will work. TODO(chandler37): Investigate ways to connect a
Discord account to an existing account.

## Encryption

The to-do list is stored in a
[Fernet](https://cryptography.io/en/latest/fernet/)-encrypted field in the
database. The key is stored in a Heroku config variable. An attacker would have
to break into both places to read your data.

The Django server is set up to require the use of SSL (HTTPS) at all times.

## Third-Party Login

Just set the environment variable `USE_ALLAUTH` to `True` (see `heroku config:set`)
if you want to support login via Slack, Google, Facebook, Discord, and
Amazon. You must use the admin interface to enter your client ID and client
secret for each service. Anyone will be able to sign up even without an email
address (that's configurable) and password resets will be possible via email if
you've signed up for the Sendgrid heroku addon. Set the environment variable
`SENDGRID_API_KEY` appropriately.

## Security Updates

You might want to subscribe to
https://groups.google.com/forum/#!forum/django-allauth-announce if you're
setting `USE_ALLAUTH` to `True` and the django announce list. TODO: How to stay
updated on Fernet bugs?

## Sentry

[Sentry](https://sentry.io/) is a closed-source commercial product that
collects unhandled exceptions in production.

To use it, which may or may not incur ongoing fees, sign up, create a Django
Sentry project, and then run the following:

`heroku config:set "SENTRY_DSN=https://yourinfo@sentry.io/yourprojectid"`

Test it by hitting `/todo/fivehundred1423457234` in your browser which will
cause an unhandled `ZeroDivisionError`.

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
- https://github.com/pennersr/django-allauth
- https://github.com/sklarsa/django-sendgrid-v5

## Future Directions -- Help Wanted

grep the code for TODOs using `grepme.sh`.

Wouldn't it be nice if we had the following:

- A login page that doesn't change style upon an invalid login
- [Docker support](https://docs.docker.com/compose/django/)
- Voice integration with Alexa, Siri, Google Home, etc.
- SPA: A better web app than the one found here, something slick like the
  'mail.google.com' interface to GMail, possibly in Angular or AngularDart or
  using React. There is an API (unimplemented but specified clearly in
  `todo/views.py`) called `mergeprotobufs` that would be at the heart of such a
  single-page application (SPA). Instead of RESTful APIs for Actions, Projects,
  Contexts, Folders, Notes, etc., there will simply be `mergeprotobufs` which
  deals with all of the data at once, merging changes made in the SPA with
  changes made otherwise (via Alexa, Slack, Discord, the CLI, this django
  classic web architecture web app, the iOS app, or the Android app). Using
  this API requires sending a protobuf from Javascript, so see
  https://github.com/protocolbuffers/protobuf/tree/master/js
- Expanding the setup.py magic built around <https://github.com/chandler37/immaculater-cli>
   into a proper PyPI package listed publicly
- An iOS app. Google's Flutter framework (which also works for Android) uses
  Dart which is a supported language for protocol buffers, so the
  aforementioned `mergeprotobufs` API will do the trick in terms of syncing
  data with other apps (like this django classic web architecture web app or a
  future SPA). React Native might be able to use generated Javascript
  protobufs, too, and targets Android as well.
- An Android app
    - Flutter? (See above about iOS.)
    - Or if you abandon iOS, perhaps SL4A scripting layer for android, or....
    - See kivy.org which uses python-for-android under the hood, particularly the
      'notes' tutorial app.
        - Dependence: Cython-0.22
        - Beware of https://www.bountysource.com/issues/7397452-cython-0-22-does-not-compile-master
            - Workaround: Replace 'except *' with ''
        - `~/git/kivy/examples/tutorials/notes/final$ buildozer -v android debug`
        - `~/git/kivy/examples/tutorials/notes/final$ buildozer -v android debug deploy run`
- An actual filesystem (remember how Plan 9 made pretty much everything pretend
  to be a filesystem? We already are pretending.) Starting with a linux
  filesystem (see FUSE) and an MacOS filesystem (see [FUSE for macOS](https://osxfuse.github.io/))
- Per-user encryption. We already use [Fernet](https://cryptography.io/en/latest/fernet/)
  to encrypt the to-do list, but some users would prefer a
  second layer of encryption such that an attacker would have to break a
  user's password to see the user's data. Resetting passwords would erase
  all data.

## Copyright

Copyright 2019 David L. Chandler

See the LICENSE file in this directory.

## Getting Things Done®

Immaculater is not affiliated with, approved or endorsed by David Allen or the
David Allen Company. David Allen is the creator of the Getting Things Done®
system. GTD® and Getting Things Done® are registered trademarks of the David
Allen Company. For more information on that company and its products, visit
GettingThingsDone.com
