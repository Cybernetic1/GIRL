# GIRL

[0. Introduction](https://github.com/Cybernetic1/GIRL#0-introduction) 

[1. Genetic Algorithm](https://github.com/Cybernetic1/GIRL#1-genetic-algorithm)

 * Pittsburgh vs Michigan approach
 * Standard Evolutionary Algorithm
 * Structure of the Genome
 * Code borrowed from...
 
[2. Evolution of Logic Rules](https://github.com/Cybernetic1/GIRL#2-evolution-of-logic-rules)

* Structure of a Rule
* Flow Chart for Generating Random Logic Formulas
* Scoring of Rules
* Score Updating from the Reinforcement-Learning Perspective
* Running the Code
* Why It Fails to Converge?

[3. Rete algorithm](https://github.com/Cybernetic1/GIRL#3-rete-algorithm)

* Understanding Rete
* Implementation Details
* For Each Game Move (play_1_move function)
* Trying the Rete Demos
 
[4. Graphical Interface for Tic Tac Toe](https://github.com/Cybernetic1/GIRL#5-graphical-interface-for-tic-tac-toe) 

## 0. Introduction

GIRL = **G**enetic **I**nduction of **R**elational **R**ules.

This is my attempt to use genetic programming to learn first-order logic rules to solve the game of Tic Tac Toe. 


It also makes use of the **Rete** production system for logic inference.

So far it has not been successful in solving Tic Tac Toe, but I think it's getting close &#128578;

## 1. Genetic Algorithm

### Pittsburgh vs Michigan approach

My algorithm is special in that it evolves an entire **set** of logic rules to play a game, where each rule has its own fitness value.  This is called the "**Michigan**" approach.  See the excerpt below:

![]([Freitas]_quote_1.jpg)

![]([Freitas]_quote_2.jpg)

### Standard Evolutionary Algorithm

* Initialize population
* Repeat until success:
    - Select parents
    - Recombine, mutate
    - Evaluate
    - Select survivors

### Structure of the Genome

 * The **genome** is a set of rules, which evolve co-operatively.
 * Each **candidate** = just one rule.
 * Each **rule** = [ head => tail ]
 * Heads and tails are composed from "var" symbols and "const" symbols.
 
 Is it OK for rules to have variable length?  Yes, as long as their lengths can *decrease* during learning.

### Code borrowed from...

This very simple genetic programming demo is translated from Ruby to Python from the book _Clever Algorithms_ by Jason Brownlee:

![Clever Algorithms](Clever_Algorithms_cover.jpg)

Run via (note: always use Python3):

    python genetic_programming_[original-demo].py

This code is the **predecessor** of my code.

## 2. Evolution of Logic Rules

### Structure of a Rule

 * pre-condition => post-condition
 * pre-condition = list of positive/negative atoms, followed by an NC part
 * NC = NC[ list of atoms... ]
 * post-condition = just one positive atom
 * literal = atomic proposition optionally preceded by a negation sign

In this version we use rules that are compatible with Rete, that consist only of conjunctions, negations, and negated conjunctions (NC).  NCs can be nested to any level. 

So the general form of a rule is: a conjunction, followed by some negated atoms, followed by a possibly nested NC.

### Flow chart of logic formula generation

This flow chart helps to understand the code in `GIRL.py`:

![Flow chart](program-flow-chart_resized.png)

### Scoring of Rules

 * For each generation, rules should be allowed to fire plentifully
 * Some facts lead to rewards

Once generated, a KB (knowledge base, = set of rules) would be run over many games:

   * For each game, a positive/negative reward would be obtained
   * That reward would be assigned to the entire inference chain (with time-discount)
   * Over many runs, each candidate rule would accumulate some scores

How the **fitness score** is calculated for each KB:

   * moves are saved during a game
   * at game's end, moves (ie. logic rules) are added or subtracted scores
   * the **average fitness** is simply averaged over the entire population of rules


Note:  In the inference engine *Clara Rules* (not used here), chains of inference can be inspected.

### Score Updating from the Reinforcement-Learning Perspective

* For each inferred post-cond, the rule.fire += ε
* Then for each time step, the "fire" values of every rule **amortize**.
* At the time of **reward**, we reward all rules that has recently fired.
* A question is: If a rule recently fired, but has no influence on the rewarded rule?
* The point is: at least I can more easily detect the antecedents during backward chaining.
* Another problem: what about instantiations? So the "fire" should be recorded as instantiated **post-conds** of a rule.
* Recording all instantiations of post-conds may be costly but there seems no other alternatives.

Another question is how to express the **Bellman Condition** or update formula.

* The "state" would be the WM for each inference step.
* The "action" would be the inference post-cond.
* So the Bellman condition says: V(x) = Expect[ R +  γ V(x') ]
* which means we have to establish a value function over the **states** x = WM contents.
* But this is different from value functions over **rules**.
* The rules are more like **actions** taking a state to a new state.
* So how come I am evaluating actions instead of states?
    - Perhaps it is a kind of Q-learning?  Q(a|x).
    - Bellman update formula:  V(x) += η[ R + γ V(x') - V(x) ]
    - for Q-learning:  Q(x,a) += η[ R + γ max Q(x',a') - Q(x,a) ]
    - for SARSA: Q(x,a) += η[ R + γ Q(x',a') - Q(x,a) ]

### Running the GIRL Code

You can try the current version:

    python GIRL.py

The randomly generated logic rules are like this, for example:

![](logic_rules_screenshot.png?)

where

* grey = conjunction
* green = negated conjunction
* bright green = conclusion
* bright red = conclusion that is also action

### Why It Fails to Converge?

The current algorithm _fails_ to converge for Tic-Tac-Toe:

![](run-results.png)

Failure is probably because the current algorithm performs only 1 inference step per game move.  I predict that Tic-Tac-Toe can be solved once we have **multi-step** inference.

## 3. Rete algorithm

### Understanding Rete

Rete is a notoriously complicated algorithm, although its basic idea is simple:  compile logic rules into a decision-tree-like network, so that rules-matching can be performed efficiently.

The PhD thesis [[Doorenbos 1995].pdf](basic_Rete_algorithm_[Doorenbos1995].pdf) is also included in this repository.  It explains the basic Rete algorithm very clearly and provides pseudo-code.  NaiveRete is based on the pseudo-code in this paper, in particular Appendix A.

There is also a paper, originally in French, which explains Rete in more abstract terms, which I partly translated into English: [[Fages and Lissajoux 1992].pdf](Fages_Lissajoux1992.pdf).

This is an example of a Rete network (with only 1 logic rule):

![example Rete network](rete_graph_ncc_test.png)

## Implementation Details

Rete is like a minimalist logic engine.  The version we use here is called **NaiveRete**, from Github: [https://github.com/GNaive/naive-rete](https://github.com/GNaive/naive-rete).

The original NaiveRete code has a few bugs that I fixed with great pain, and with the help of Doorenbos' thesis.

For our purpose, any inference engine will do.  Rete is not necessary;  It mere provides faster inference speed.  For example, Genifer 3 is another simple rule engine.  Genifer 6 is based on Rete.

1. First, evolve a set of rules, import into Rete
2. Run the rules for N iterations, record scores
3. Repeat

Rete-related ideas:

* If Rete is used, we may want to learn the Rete network directly
* How to genetically encode a Rete net?
* Perhaps differentiable Rete is a better approach?
* It may be efficient enough to compile to Rete on each GA iteration 

### For Each Game Move (play_1_move function)

1. REPEAT: apply rules and collect all results
	Update Rete Working Memory (WM)

2. Select 1 playable result and play it
	Each rule candidate could have multiple instances

Should we add all P~i~'s to WM?

1. Every rule may infer a (non-action) proposition P~i~

2. Every rule has its instantiations that should be assumed
    - Why are instantiations different? because of substitution into rules.
    - But are these subsitutions mutually compatible or exclusive?
    - Seems compatible, eg: all men are mortal => Socrates and Plato are mortal.
    
3. Can we simply accept all such propositions in the same Working-Memory state?
    - In other words, if head[0] == P then we always add postcond to WM.

4. TO-DO:  we can iterate the "**inference**" step multiple times, before making an action.

NOTE: When a variable is unbound, we simply assign random values to it; This seems reasonable, as we regard unbound predicates as **stochastic**.

### Trying the Rete Demos

Here are some demos:

    python genifer.py
    python genifer_lover.py

You can also look into the `tests/` directory for examples.

To run the Rete tests, first install PyTest via:

    pip3 install pytest

And then:

    python -m pytest test/*_test.py

## 4. Graphical Interface for Tic Tac Toe

The GUI is like this:

![](GUI-screenshot.png)

It requires **PyGame**:

    sudo apt install python3-pygame

I will prepare a version that does not use a graphic interface.
