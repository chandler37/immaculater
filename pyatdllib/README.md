# pyatdl

This is pyatdl (pronounced "PEE-ott"), a python implementation of yet another
to-do list. pyatdl is the core of Immaculater. See the parent directory to find
Immaculater.

## Dependencies and Installation

See [`README.md`](https://github.com/chandler37/immaculater/blob/master/README.md)
in the parent directory regarding using `virtualenv` and `pip install -r
requirements.txt` (inside an activated virtualenv). That will install some of
the software below. You will still need to do `pip install pylint coverage`
(inside an activated virtualenv).

We depend on the following:

 - [protoc](https://developers.google.com/protocol-buffers/) -- It's what builds
  `pyatdl_pb2.py` which you must check in whenever you modify `pyatdl.proto`.
 - [appcommands](https://github.com/google/google-apputils)
 - [gflags](https://github.com/gflags/python-gflags)
 - python protobufs

Optional installs include the following:

 - [coverage]( http://nedbatchelder.com/code/coverage)
 - [pylint](http://www.pylint.org/)
 - [pychecker](http://pychecker.sourceforge.net/)

To see if you have the core dependencies, run the test cases with the following:

 - `make test`

To see if you have all optional dependencies, run the following:

 - `make test pychecker pylint cov`

## Dogfooding a.k.a. Running `ui/immaculater.py`

We're so early in development that dogfooding is a heroic act. To dogfood this,
use Immaculater from the parent directory -- it has a command-line interface
(CLI) built in. Alternatively, using just this directory, there is a true CLI
-- from this directory, type the following:

 - `bash runme.sh help`
 - Now you understand better what this does:
 - `bash runme.sh interactive`

The following is an example interactive session:

 - `immaculater> cd /inbox`
 - `immaculater> mkact "Remember the yogurt"`
 - `immaculater> mkctx "@Store"`
 - `immaculater> chctx @Store 'Remember the yogurt'`
 - `immaculater> inctx @Store`
 - `--action--- uid=5 --incomplete-- 'Remember the yogurt'`
 - `immaculater> help`

If you want to script something, keep in mind tricks like the following:

 - `echo ls | bash runme.sh batch /dev/stdin`
 - `--project-- uid=1 --incomplete-- inbox`
 - `--project-- uid=4 --incomplete-- PPP`

## TODOs

TODO(chandler): Add `setup.py`; research 'pip' and 'easy_install'
