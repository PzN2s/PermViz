# PermViz - Linux Permission Editor

> Developed by **DEV:Reham**

A terminal tool that lets you view and edit Linux file permissions through a clean, interactive interface.

## What it does

Instead of using chmod commands from the terminal, PermViz opens a text UI where you can:

- Toggle Read, Write, and Execute permissions for Owner, Group, and Other using checkboxes
- See the octal value update live as you toggle
- Read a clear explanation of what each permission means and its numeric value
- Preview file contents before making changes
- Get warnings before setting dangerous permissions

## How to install

```
git clone https://github.com/PzN2s/PermViz.git
cd PermViz
pip install textual
```

## How to use

```
python3 main.py <filepath>
```

Example:
```
python3 main.py /etc/passwd
```

## Requirements

- Python 3.8+
- textual (installed via pip)

## Works on

Any Linux distribution with Python 3: Ubuntu, Debian, Fedora, Arch, Alpine, openSUSE, Gentoo, NixOS, and more.

## Links

GitHub: https://github.com/PzN2s/PermViz
