# Crossword AI
My project is an optimal classical AI algorithm that generates solutions to inputted puzzles using
the constraint satisfaction problem with node consistency, arc (edge) consistency, custom heuristics (re: specifications for `generate.py` for more information), and backtracking search while utilizing S.O.L.I.D. design and algorithmic complexity principles.

The constraints that must be satisfied are as follows: 
- Unary Constraints: The word must match the specified length for each variable.
- Binary Constraints: Variables may overlap, entailing that certain characters must be the same at overlapping positions between neighboring words.
- Uniqueness Constraint: All words must be different from each other.

## Motivation for project:
I am interested in algorithmic-heavy and optimization-heavy projects as I like to think myself foremost a computer scientist. This project involved using custom heuristics that cannot be solved via proofs (hence heuristic), backtracking algorithm that can be illustrated as a tree of potential state spaces, and thus can be optimized through interleaved arc consistency enforcement through inference (which is a nice homage to my background in philosophy) to minimize the nodes needed to be traversed to reach a solution, if any. It also involves the notion of artificial intelligence (specifically classical), which I find to be a fascinating subset of computer science and mathematics.
  
## Background Context:
The data file contains structures 0-2 and words 0-2 in .txt format that are used as inputs when running the program. The `crossword.py` creates the crossword itself by creating a 2D matrix/grid given the inputted structure and potential words. `generate.py` begins the simulation and is the crux of the program. Each function in generate.py that I was responsible for is commented to illustrate my thought process, optimizations when present (e.g. select unassigned function), and what those optimizations saved/made efficient (e.g. backtracking search employing inference to reduce state space saving auxiliary time and reducing the recursive stack, but at the cost of auxiliary space created from deepcopying the domain).

`crossword.py` and a smaller portion of `generate.py` contains ancillary functions provided by the CS50AI team. The `crossword.py` file defines two key classes: Variable and Crossword. The `Variable` class represents a blank input position for a word in the grid and has four properties: the row (i), column (j), direction (either `Variable.ACROSS` or `Variable.DOWN`), and word length. The Crossword class represents the entire puzzle.

In `generate.py`, `CrosswordCreator` is a class that is used to solve the crossword puzzle with a `Crossword` object property and a domain property. The domain property is a dictionary that maps variables to the set of potential words inputted when running the program.

To see what functions I was responsible for, please refer to the specifications below. In essence, all functions besides `main` below the `solve` function was implemented and optimized by myself. The design was mostly left up to us with the caveat of certain constraints/limitations imposed by CS50AI team's design and the interaction of functions thereof. 

## Specifications for generate.py:
`enforce_node_consistency` function updates self.domains such that each variable is node consistent.

`revise` makes the variable `x` arc consistent with the variable `y`.

`ac3 function`, using the AC3 algorithm, enforces arc consistency on the problem, which is achieved when all the values in each variable’s domain satisfy that variable’s binary constraints.

`assignment_complete` function checks if the assignment dict given has a value for all variables in the crossword.

`consistent` function checks if an assignment dict's variables all have valid values that are node consistent, edge consistent, and are distinct.

`order_domain_values` function returns a list of all of the values in the domain of var, ordered according to the least-constraining values heuristic. The least-constraining values heuristic is choosing a potential value that eliminates the least words in other domains. The motivation is borne from the rationality that a solution is more likely guaranteed if there are more potential answers to choose from for each node.

`select_unassigned_variable` function returns a single variable in the crossword puzzle that is not yet assigned by assignment, according to the minimum remaining value heuristic and then the highest degree heuristic. The minimum remaining value heuristic chooses a variable with the least potential words. The motivation is that we will likely reach a solution (or not) faster if we have one less variable to choose from by exhausting those choices. The motivation for the degree heuristic is that we can likely reach a solution (or not) faster if we affect the most neighboring nodes by choosing potential words within the domain of a specific node.

`backtrack` function accepts an assignment as input and returns a complete satisfactory assignment of variables to values if it is possible to do so, or None otherwise. It is optimized using the `ac3` algorithm by reducing the state space/potential nodes in the backtracking tree.

## Usage example:
`python generate.py data/structure1.txt data/words1.txt` in command line.
Prerequisite for generation of an image file of a given assignment per `save` function: download pillow using `pip3 install Pillow`.

## What I learned:
This project was a great learning experience for learning to work within the requirements and limitations imposed by other collaborators' code and design (in this case, the CS50AI team). This project gave me an opportunity to understand a foreign codebase, relation between functions, and their design and to interact with it cohesively. It also allowed me to employ my understanding of modularity and abstraction, readability and clean code, and to seek insight into why the CS50AI team chose certain inputs and outputs (e.g. `ac3` allowing an `arcs` argument in order to start with a different queue of edges for backstracking optimization). 

### Thank you for visiting my project. 
