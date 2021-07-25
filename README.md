<font size="5"> 

# GILR

Genetic Inductive Learning of Logic Rules

Genetic programming code (borrowed)
====================================

This very simple genetic programming demo is translated to Python (from Ruby) from the book _Clever Algorithms_ by Jason Brownlee:

![Clever Algorithms](Clever_Algorithms_cover.jpg)

Run via (note: always use Python3):

    python genetic_programming_1.py

This code is the predecessor of my code.

Flow chart of logic formula generation
======================================

![Flow chart](program-flow-chart_resized.png)

<img src="https://github.com/Cybernetic1/GILR/raw/master/program-flow-chart_resized.png" width=100% height=100%>

Rete algorithm
==============

Rete is like a minimalist logic engine.  The version we use here is called NaiveRete, from Github:

https://github.com/GNaive/naive-rete

Here are some demos:

    python genifer.py
    python genifer_lover.py

You can also look into the `tests` directory for examples.

Rete is a notoriously complicated algorithm, although its basic idea is simple:  compile logic rules into a decision-tree-like network, so that rules-matching can be performed efficiently.

This is an example of a Rete network (with only 1 logic rule):

![example Rete network](rete_graph_ncc_test.png)

The PhD thesis [[Doorenbos 1995].PDF](basic_Rete_algorithm_[Doorenbos1995].pdf) is also included in this repository.  It explains the basic Rete algorithm very clearly and provides pseudo-code.  NaiveRete is based on the pseudo-code in this paper, in particular Appendix A.

There is also a paper, originally in French, which explains Rete in more abstract terms, which I partly translated into English: [[Fages and Lissajoux 1992].PDF](Fages_Lissajoux1992.pdf).

The original NaiveRete code has a few bugs that I fixed with great pain, and with the help of Doorenbos' thesis.

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

 </font>