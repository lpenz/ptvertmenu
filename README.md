[![CI](https://github.com/lpenz/ptvertmenu/actions/workflows/ci.yml/badge.svg)](https://github.com/lpenz/ptvertmenu/actions/workflows/ci.yml)
[![coveralls](https://coveralls.io/repos/github/lpenz/ptvertmenu/badge.svg?branch=main)](https://coveralls.io/github/lpenz/ptvertmenu?branch=main)
[![PyPI](https://img.shields.io/pypi/v/ptvertmenu)](https://pypi.org/project/ptvertmenu/)

# ptvertmenu

Vertical menu widget for prompt-toolkit with optional fzf-inspired search


## Installation


### Releases

ptvertmenu can be installed via [pypi]:

```
pip install ptvertmenu
```

For [nix] users, it is also available as a [flake].


### Repository

We can also clone the github repository and install ptvertmenu from it with:

```
pip install .
```

We can also install it for the current user only by running instead:

```
pip install --user .
```


## Development

ptvertmenu uses the standard python3 infra. To develop and test the module:
- Clone the repository and go into the directory:
  ```
  git clone git@github.com:lpenz/ptvertmenu.git
  cd ptvertmenu
  ```
- Use [`venv`] to create a local virtual environment with
  ```
  python -m venv venv
  ```
- Activate the environment by running the shell-specific `activate`
  script in `./venv/bin/`. For [fish], for instance, run:
  ```
  source ./venv/bin/activate.fish
  ```
- Install ptvertmenu in "editable mode":
  ```
  pip install -e '.[test]'
  ```
- To run the tests:
  ```
  pytest
  ```
  Or, to run the tests with coverage:
  ```
  pytest --cov
  ```
- Finally, to exit the environment and clean it up:
  ```
  deactivate
  rm -rf venv
  ```


[pypi]: https://pypi.org/project/ptvertmenu/
[nix]: https://nixos.org/
[flake]: https://nixos.wiki/wiki/Flakes
[`venv`]: https://docs.python.org/3/library/venv.html
