GIRL
====

GIRL = **G**enetic **I**nduction of **R**elational **R**ules.

This is my attempt to use genetic programming to learn first-order logic rules to solve the game of Tic Tac Toe. 


It also makes use of the **Rete** production system for logic inference.

So far it has not been successful in solving Tic Tac Toe, but I think it's getting close &#128578;

1. Code borrowed from...
-----------------------

This very simple genetic programming demo is translated from Ruby to Python from the book _Clever Algorithms_ by Jason Brownlee:

![Clever Algorithms](Clever_Algorithms_cover.jpg)

Run via (note: always use Python3):

    python genetic_programming_[original-demo].py

This code is the **predecessor** of my code.

2. Pittsburgh vs Michigan approach
-------------------------------

My algorithm is special in that it evolves an entire **set** of logic rules to play a game, where each rule has its own fitness value.  This is called the "**Michigan**" approach.  See the excerpt below:

![]([Freitas]_quote_1.jpg)

![]([Freitas]_quote_2.jpg)


3. Flow chart of logic formula generation
--------------------------------------

This flow chart helps to understand the code in `GIRL.py`:

![Flow chart](program-flow-chart_resized.png)
 
4. Rete algorithm
--------------

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

5. Genetic evolution of logic Rules
--------------------------------

You can try the current version:

    python GIRL.py

The randomly generated logic rules are like this, for example:

![](logic_rules_screenshot.png)

where

* grey = conjunction
* green = negated conjunction
* red = conclusion

The current algorithm _fails_ to converge for Tic-Tac-Toe because the rules the current algorithm performs only 1 inference step per game move.  I predict that Tic-Tac-Toe can be solved once we have multi-step inference.

6. How to run the Rete tests
---------------------

Install PyTest via:

    pip3 install pytest

And then:

    python -m pytest test/*_test.py


7. GyGame GUI dependency
---------------------

The GUI is like this:

![](GUI-screenshot.png)

It requires PyGame:

    sudo apt install python3-pygame

I will prepare a version that does not use a graphic interface.