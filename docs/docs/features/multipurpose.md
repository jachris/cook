---
layout: docs
title: Multipurpose
---

# Multipurpose
{:.no_toc}

* TOC
{:toc}


## Overview

Rules are not bound to any specific language. Unlike many other tools
you do not globally declare that you are building a C++ project --- instead you 
just use the rules provided by the `cpp` module. Many other rules are planned, 
some already exist. While not provided at the moment, there should be rules to 
automatically export images from your favorite image editor so that you can
embed them in your LaTeX paper for example. Or you should be able to build a C 
library that you could use in your Rust project or the other way around.

This means Cook wants to be a build system you can use in many situations: 
Whether you are writing a new game, a new paper, developing a website or just
working on a very simple C++ project --- you should be covered.


## Outlook

Right now the plan is to host all these rules inside the main repository, but
this might change depending on how things are going. It is however desirable
that either Cook comes with many builtin rules which should provide almost
everything one could need for automating any kind of build or there should be
an easy way to download and manage other rule sets.
