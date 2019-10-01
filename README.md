# GILR
Genetic Inductive Learning of Logic Rules

NOTE: always use Python3

Very simple genetic programming demo
====================================

The simple demo is translated to Python (from Ruby) from the book _Clever Algorithms_ by Jason Brownlee:

![Clever Algorithms](Clever_Algorithms_cover.jpg)

Run by:

    python genetic_programming_1.py

This code is the predecessor of my code.

Rete algorithm
==============

Rete is like a minimalist logic engine.  The version we use here is called NaiveRete, from Github:

https://github.com/GNaive/naive-rete

Here are some demos:

    python genifer.py
    python genifer_lover.py

You can also look into the `tests` directory for examples.

The PhD thesis `[Doorenbos 1995].PDF` is also included in this repository.  It explains the basic Rete algorithm very clearly and provides pseudo-code.  NaiveRete is based on the pseudo-code in this paper, in particular Appendix A.

Genetic evolution of logic Rules
================================

You can try the current version:

    python genetic_programming.py

The randomly generated logic rules are like this:

![](logic_rules_screenshot.png)

where

* white = conjunction
* green = negated conjunction
* red = conclusion

The current algorithm _fails_ to converge for Tic-Tac-Toe because the rules are 'flat' in the sense that they don't support new predicate invention.  That means the current logic performs only 1 inference step per game move.  I predict that Tic-Tac-Toe can be solved once we have multi-step inference, with predicate invention.

How to run tests (for Rete)
===========================

Install PyTest via:

    pip3 install pytest

And then:

    python -m pytest test/*_test.py


GyGame GUI dependency
=====================

The GUI is like this:

![](GUI-screenshot.png)

It requires PyGame:

    sudo apt install python3-pygame

I will prepare a version that does not use a graphic interface.
