---
layout: docs
title: Install
---

# Installation
{:.no_toc}

Before using Cook, please note that it should not be considered stable and it
is not ready for production use.

* TOC
{:toc}


## Users

You can install Cook using `pip3`.

```bash
sudo apt-get install python3  # If you are using Ubuntu.
pip3 install https://github.com/jachris/cook/archive/master.zip
````

If you want to update to the newest version, run

```bash
pip3 install https://github.com/jachris/cook/archive/master.zip --upgrade
````


## Contributors

You will need `git` and `Python3`.

```bash
$ sudo apt-get install git python3  # If you are using Ubuntu.
$ git clone https://github.com/jachris/cook
$ cd cook
$ ./setup.py develop   # If you are using Unix, OR
$ py setup.py develop  # If you are using Windows
```

If you want to update to the newest version you just have to `git pull` since
you have used the `develop` mode.
