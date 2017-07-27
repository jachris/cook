---
layout: default
title: Home
---

⚠ This software is currently in <span style="color:red">_**alpha phase**_</span> and <span style="color:red">_**not ready for production use**_</span>. The API should not be considered stable. The website is not very polished. I just tried to get the product out as soon as possible, since I wanted to release it early. Expect many improvments in the near future, especially on the documentation.

---

# Overview

Cook is yet-another build-system, but it tries to do things differently by 
focusing on you – the user. It was written with a focus on the simplicity of
creating custom rules. Rules are not defined by commands, but rather arbitrary
Python code, which makes it very easy to manage a custom solution. Don't worry
if you don't know the Python programming language. It should still be very 
straightforward to get a working build going.

Go [here](/docs/getting-started/) to get started.

# Why choose Cook?

There are many reasons why you should check it out.

* **Fast builds.** We spawn an appropriate amount of parallelized workers
chosen based on the number of cores available and also make use of the concept 
of incremental building, which means that only files that have to be rebuild 
are actually done again.

* **Easy extensibility.** The system, including the builtin rules, are entirely 
written in Python. Writing custom rules is very easy thanks to Python's 
generator concept. Custom rules have the same power available as builtin ones.

* **Platform independence.** The Python ecosystem is known for it's cross-platform 
solutions. Your rules can run everywhere. On top of that, all builtin rules
will work on most platforms, which means you do not have to worry about 
platform-specific compiler incantation and are free to focus on your project 
instead.

* **Multipurpose tool.** Cook is not only for code writers, but everyone who
benefits from some kind of automation. It can compile your LaTeX documents,
save documents as PDFs or even export images from your favorite image editor.

More reasons can be found [here](/comparison/).
