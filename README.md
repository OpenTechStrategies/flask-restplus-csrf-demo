# `flask-restplus-csrf` demo

This is a small example project to demonstrate usage of
 [flask-restplus-csrf](https://github.com/OpenTechStrategies/flask-restplus-csrf).

See the doc string at the top of [demo.py](demo.py) for a detailed
description of exactly what is being demonstrated.  To see the demo in
action, there's a bit of setup required.

If you have python3.6.3 installed, you are good to go.  If you don't,
then you'll need to install it.  One way to do that is with `pyenv`; see
https://gioele.io/pyenv-pipenv for a great introduction to pyenv, and
maybe see https://github.com/pyenv/pyenv-installer for a convenient
installer.

The rest of these instructions assume that you have installed `pyenv`
and that you're going to use it to obtain and run Python 3.6.3.  If
you already have Python 3.6.3 by other means, it should be pretty
clear which steps below you can skip.

Using `pyenv` to get Python 3.6.3 looks something like this:

```
  # Make sure you have the prerequisites for building Python.  The
  # list of packages for Debian and Ubuntu as of this writing is
  # below, but check https://github.com/pyenv/pyenv/wiki for an
  # up-to-date list of packages.
  $ sudo apt-get install -y make build-essential libssl-dev zlib1g-dev \
         libbz2-dev libreadline-dev libsqlite3-dev wget curl llvm \
         libncurses5-dev libncursesw5-dev xz-utils tk-dev libffi-dev \
         liblzma-dev python-openssl git libedit-dev

  # Install pyenv
  $ curl -L https://raw.githubusercontent.com/pyenv/pyenv-installer/master/bin/pyenv-installer | bash

  # It will give you some instructions to put in your .<shell>rc file, but you can
  # just execute on the CLI
  $ export PATH="/home/admin/.pyenv/bin:$PATH"
  $ eval "$(pyenv init -)"
  $ eval "$(pyenv virtualenv-init -)"

  # Now you can install Python 3.6.3 via pyenv.
  $ pyenv install 3.6.3
```

Start running Python 3.6.3 in your current shell:

```
  $ pyenv global 3.6.3
```

Once you're running Python 3.6.3 in this shell, make sure you have a
compatible `pipenv` installed too via pip or apt:

```
  $ pip3 install pipenv
  # or
  $ sudo apt-get install pipenv
```

Now you can set up and install Flask-RESTPlus-CSRF:

```
  $ pipenv --python 3.6.3 install
  $ pipenv install -e git+https://github.com/OpenTechStrategies/flask-restplus-csrf@master#egg=flask-restplus-csrf
```

### Run the demo


```
  $ pipenv run ./demo.py
  $ curl http://127.0.0.1:5000/hello
```

and then point your browser at http://localhost:5000/web.

### Running the tests


First get dependencies:

```
  $ pipenv install simplejson requests pytest
```

While [demo.py](demo.py) is running, you can also do

```
  $ pipenv run  ytest test_demo.py
```

to run a series of tests that verify that
[flask-restplus-csrf](https://github.com/OpenTechStrategies/flask-restplus-csrf)
is working correctly.
