# Student Tracker

A small tool for teachers to enter students, compute the average score, assign a grade, search by name, and edit or delete records. Data is stored in SQLite and remains available the next time the program opens.

## Requirements

- Python 3.12.15, the version recorded in `.python-version`
- [pyenv](https://github.com/pyenv/pyenv) on macOS and Linux, [pyenv-win](https://github.com/pyenv-win/pyenv-win) on Windows
- The `virtualenv` tool to create `.venv`
- Tcl/Tk 8.6 so the Tkinter window can open

A Python built by pyenv includes Tkinter only when Tcl/Tk 8.6 is present at build time. Python 3.12 uses Tk 8.6.

## Install pyenv

### macOS

```bash
brew install pyenv tcl-tk@8
```

Add `pyenv init` to `~/.zshrc` using the instructions printed at the end of `brew install`, then open a new terminal.

### Linux

Install the build tools and Tk, then install pyenv.

Debian / Ubuntu:

```bash
sudo apt update
sudo apt install -y make build-essential libssl-dev zlib1g-dev \
  libbz2-dev libreadline-dev libsqlite3-dev curl git \
  libncursesw5-dev xz-utils tk-dev libxml2-dev libxmlsec1-dev \
  libffi-dev liblzma-dev
curl https://pyenv.run | bash
```

Fedora:

```bash
sudo dnf install -y make gcc zlib-devel bzip2 bzip2-devel readline-devel \
  sqlite sqlite-devel openssl-devel tk-devel libffi-devel xz-devel git curl
curl https://pyenv.run | bash
```

Arch:

```bash
sudo pacman -S --needed base-devel openssl zlib xz tk git curl
curl https://pyenv.run | bash
```

Add this to `~/.bashrc` or `~/.zshrc`, then open a new terminal:

```bash
export PYENV_ROOT="$HOME/.pyenv"
export PATH="$PYENV_ROOT/bin:$PATH"
eval "$(pyenv init -)"
```

### Windows

Upstream pyenv does not run natively on Windows. Use pyenv-win from PowerShell:

```powershell
Invoke-WebRequest -UseBasicParsing -Uri "https://raw.githubusercontent.com/pyenv-win/pyenv-win/master/pyenv-win/install-pyenv-win.ps1" -OutFile "./install-pyenv-win.ps1"; &"./install-pyenv-win.ps1"
```

Close the terminal and open it again. The Python build installed by pyenv-win comes from python.org and already includes Tkinter, so Tcl/Tk does not need a separate install.

## Install Python 3.12.15

Run these commands from the project directory.

### macOS

The Homebrew `tcl-tk` package is often version 9. Python 3.12 needs `tcl-tk@8`:

```bash
export PATH="$(brew --prefix tcl-tk@8)/bin:$PATH"
export LDFLAGS="-L$(brew --prefix tcl-tk@8)/lib"
export CPPFLAGS="-I$(brew --prefix tcl-tk@8)/include"
export PKG_CONFIG_PATH="$(brew --prefix tcl-tk@8)/lib/pkgconfig"
export PYTHON_CONFIGURE_OPTS="--with-tcltk-includes='-I$(brew --prefix tcl-tk@8)/include' --with-tcltk-libs='-L$(brew --prefix tcl-tk@8)/lib -ltcl8.6 -ltk8.6'"

pyenv install 3.12.15
pyenv local 3.12.15
```

### Linux and Windows

On Linux, the `tk-dev`, `tk-devel`, or `tk` package from the step above is enough for the build to include Tkinter.

```bash
pyenv install 3.12.15
pyenv local 3.12.15
```

`pyenv local` writes `.python-version`. The next time you enter the project directory, pyenv selects Python 3.12.15.

## Create the virtualenv

Install the `virtualenv` package, then activate the environment for your system:

```bash
python -m pip install --user virtualenv
python -m virtualenv .venv
```

macOS and Linux:

```bash
source .venv/bin/activate
```

Windows Command Prompt:

```bat
.venv\Scripts\activate
```

Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

After activation, on all three systems:

```bash
python -m pip install -r requirements.txt
python -c "import tkinter; print(tkinter.TkVersion)"
```

The printed version must be `8.6`. The program runs on the Python standard library. `requirements.txt` lists PyInstaller, the package used to build the desktop app.

## Run

From the project directory, with `.venv` activated:

```bash
python -m student_tracker          # Tkinter window
python -m student_tracker --cli    # terminal menu
```

Terminal menu:

1. Add one student
2. Add many students (enter `N`, then enter each student)
3. Show the list
4. Search by name
5. Edit a student
6. Delete a student
0. Exit

When you run from source, `students.db` is created in the current directory. A packaged build writes the file as follows:

- macOS `.app`: `~/Library/Application Support/StudentTracker/students.db`
- Windows and Linux: the same folder as the executable (`StudentTracker.exe` or `StudentTracker`)

## Grades

The average is (Math + Literature + English) / 3, rounded to 2 decimal places (`ROUND_HALF_UP`).

| Average | Grade |
| --- | --- |
| 8.00 and above | Giỏi |
| 6.50 up to, but not including, 8.00 | Khá |
| 5.00 up to, but not including, 6.50 | Trung bình |
| below 5.00 | Yếu |

For example, 7.96 is Khá. The band under Giỏi continues until 8.00, so a score such as 7.96 is not cut off at 7.90.

Age must be from 1 to 120. Each subject score must be from 0 to 10.

## Sample data

**Load sample data** calls `https://dummyjson.com/users?limit=30` on a background thread, then writes SQLite on the interface thread so the window stays responsive. DummyJSON provides names and ages, not scores, so Math, Literature, and English are derived in a stable way from the user id. Loading the sample again updates those same rows.

## Tests

```bash
python -m unittest discover -s tests
```

## Package

With PyInstaller installed in `.venv`:

```bash
pyinstaller StudentTracker.spec
```

The same command works on all three systems. The spec creates a `.app` only when the build runs on macOS.

- macOS: `dist/StudentTracker.app`
- Windows: `dist/StudentTracker/StudentTracker.exe`
- Linux: `dist/StudentTracker/StudentTracker`

The packaged build opens the window and has no console. The `--cli` menu is for running from source.
