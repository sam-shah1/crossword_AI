import sys

from crossword import *


class CrosswordCreator():

    def __init__(self, crossword):
        """
        Create new CSP crossword generate.
        """
        self.crossword = crossword
        self.domains = {
            var: self.crossword.words.copy()
            for var in self.crossword.variables
        }

    def letter_grid(self, assignment):
        """
        Return 2D array representing a given assignment.
        """
        letters = [
            [None for _ in range(self.crossword.width)]
            for _ in range(self.crossword.height)
        ]
        for variable, word in assignment.items():
            direction = variable.direction
            for k in range(len(word)):
                i = variable.i + (k if direction == Variable.DOWN else 0)
                j = variable.j + (k if direction == Variable.ACROSS else 0)
                letters[i][j] = word[k]
        return letters

    def print(self, assignment):
        """
        Print crossword assignment to the terminal.
        """
        letters = self.letter_grid(assignment)
        for i in range(self.crossword.height):
            for j in range(self.crossword.width):
                if self.crossword.structure[i][j]:
                    print(letters[i][j] or " ", end="")
                else:
                    print("█", end="")
            print()

    def save(self, assignment, filename):
        """
        Save crossword assignment to an image file.
        """
        from PIL import Image, ImageDraw, ImageFont
        cell_size = 100
        cell_border = 2
        interior_size = cell_size - 2 * cell_border
        letters = self.letter_grid(assignment)

        # Create a blank canvas
        img = Image.new(
            "RGBA",
            (self.crossword.width * cell_size,
             self.crossword.height * cell_size),
            "black"
        )
        font = ImageFont.truetype("assets/fonts/OpenSans-Regular.ttf", 80)
        draw = ImageDraw.Draw(img)

        for i in range(self.crossword.height):
            for j in range(self.crossword.width):

                rect = [
                    (j * cell_size + cell_border,
                     i * cell_size + cell_border),
                    ((j + 1) * cell_size - cell_border,
                     (i + 1) * cell_size - cell_border)
                ]
                if self.crossword.structure[i][j]:
                    draw.rectangle(rect, fill="white")
                    if letters[i][j]:
                        _, _, w, h = draw.textbbox((0, 0), letters[i][j], font=font)
                        draw.text(
                            (rect[0][0] + ((interior_size - w) / 2),
                             rect[0][1] + ((interior_size - h) / 2) - 10),
                            letters[i][j], fill="black", font=font
                        )

        img.save(filename)

    def solve(self):
        """
        Enforce node and arc consistency, and then solve the CSP.
        """
        self.enforce_node_consistency()
        self.ac3()
        return self.backtrack(dict())

    def enforce_node_consistency(self):
        """
        Update `self.domains` such that each variable is node-consistent.
        (Remove any values that are inconsistent with a variable's unary
         constraints; in this case, the length of the word.)
        """

        for var in self.domains:
            # Check it's not empty.
            if not self.domains[var]:
                continue

            # Cannot remove from set during iteration, so must save to remove at end (if any).
            willRemove = set()
            for word in self.domains[var]:
                if len(word) != var.length:
                    willRemove.add(word)
            # Removing set intersection, if any.
            self.domains[var] = self.domains[var] - willRemove

    def revise(self, x, y):
        """
        Make variable `x` arc consistent with variable `y`.
        To do so, remove values from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains[y]`.

        Return True if a revision was made to the domain of `x`; return
        False if no revision was made.
        """

        if x == y:
            return False

        revised = False
        willRemove = set()
        for x_word in self.domains[x]:
            for y_word in self.domains[y]:
                # If no overlap, then there is nothing to satisfy.
                if (x_word == y_word or not self.crossword.overlaps[x, y]):
                    continue

                # Otherwise, we'll retrieve overlapping indices of each var to see if char of words match at respective indices.
                xi, yi = self.crossword.overlaps[x, y]
                if x_word[xi] == y_word[yi]:
                    break
            else:
                willRemove.add(x_word)

        if willRemove:
            revised = True
            self.domains[x] = self.domains[x] - willRemove
        return revised

    def ac3(self, arcs=None):
        """
        Update `self.domains` such that each variable is arc consistent.
        If `arcs` is None, begin with initial list of all arcs in the problem.
        Otherwise, use `arcs` as the initial list of arcs to make consistent.

        Return True if arc consistency is enforced and no domains are empty;
        return False if one or more domains end up empty.
        """

        # Using a stack instead of a deque as it's consequentially the same, as well as the same time complexity, but real
        # run time is improved as it doesn't create linear auxiliary space and iterate over inputted edges.
        if not arcs:
            arcs = []
            for var in self.domains:
                for nei in self.crossword.neighbors(var):
                    arcs.append((var, nei))

        while arcs:
            var1, var2 = arcs.pop()

            if self.revise(var1, var2):
                # If there are no available choices for var1 left, then there is no solution to crossword.
                if not self.domains[var1]:
                    return False

                # If there was a revision, then we need to check if the neighboring nodes of var1 remain consistent with var1.
                for affected_var in self.crossword.neighbors(var1) - {var2}:
                    arcs.append((affected_var, var1))

        return True

    def assignment_complete(self, assignment):
        """
        Return True if `assignment` is complete (i.e., assigns a value to each
        crossword variable); return False otherwise.
        """
        # Check if all variables are accounted for and that there is a non-empty value associated with it.
        # We can assume that each non-empty value is a str.
        for var in self.domains:
            if (var not in assignment or not assignment[var]):
                return False
        # If for loop finishes, then all assignment dictionary is complete.
        return True

    def consistent(self, assignment):
        """
        Return True if `assignment` is consistent (i.e., words fit in crossword
        puzzle without conflicting characters); return False otherwise.
        """

        # Helper function
        def neighbor_consistency(variable):
            chosen_word = assignment[variable]

            for nei in self.crossword.neighbors(variable):
                if nei not in assignment:
                    continue

                nei_word = assignment[nei]
                # All answers must be distinct; no duplicates.
                if nei_word == chosen_word:
                    return False
                # Check if char values at words are the same at overlapping crossword grid index.
                xi, yi = self.crossword.overlaps[variable, nei]
                if chosen_word[xi] != nei_word[yi]:
                    return False

            return True

        for var in self.domains:
            # Checking if all variables are accounted for, there is a value, and that value is valid via var domain.
            if (
                var in assignment and
                assignment[var] and
                assignment[var] in self.domains[var]
            ):

                # Check if value matches correct length.
                if (len(assignment[var]) != var.length):
                    return False
                # Check for any conflicts with neighboring nodes.
                if not neighbor_consistency(var):
                    return False
        return True

    def order_domain_values(self, var, assignment):
        """
        Return a list of values in the domain of `var`, in order by
        the number of values they rule out for neighboring variables.
        The first value in the list, for example, should be the one
        that rules out the fewest values among the neighbors of `var`.
        """

        # Initializing a dict count of values that are ruled out when using a specific word, for each word.
        ruled_out = {}
        for word in self.domains[var]:
            ruled_out[word] = 0

            for nei_var in self.crossword.neighbors(var):
                # Per instruction, if variable has a word assigned to it, it should not be counted.
                if nei_var in assignment:
                    continue

                for nei_word in self.domains[nei_var]:
                    if nei_word == word:
                        continue

                    xi, yi = self.crossword.overlaps[var, nei_var]
                    if word[xi] != nei_word[yi]:
                        ruled_out[word] += 1

        # Return list of words sorted per least-constraining values heuristic.
        return sorted(ruled_out, key=lambda z: ruled_out[z])

    def select_unassigned_variable(self, assignment):
        """
        Return an unassigned variable not already part of `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.
        """

        # We want the minimum of potential values via least value heuristic first, then maximum of neighbors via highest degree heuristic.
        # The code will handle edge cases of all variables having been assigned already by returning null.
        # Optimized via use of degree and potential value variables instead of creating a list, saving linear space
        # and nlogn auxiliariy time (sorting variables based on degrees and potential values).
        degree = 0
        least_potential_values = float("inf")
        return_var = None
        for var in self.domains:
            if var in assignment:
                continue

            potential_values = self.order_domain_values(var, assignment)
            val_count = len(potential_values)

            # Via least value heuristic, we want to send the variable with the least amount of possible values.
            if val_count < least_potential_values:
                least_potential_values = val_count
                return_var = var

            # If there is a tie, we will choose the one with highest neighbor count.
            elif val_count == least_potential_values:
                nei_count = len(self.crossword.neighbors(var))

            # If there is a tie, we can arbitrarily choose which var to send. For code readability, I chose to change the var.
                if nei_count >= degree:
                    least_potential_values = val_count
                    degree = nei_count
                    return_var = var

        return return_var

    def backtrack(self, assignment):
        """
        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible to do so.

        `assignment` is a mapping from variables (keys) to words (values).

        If no assignment is possible, return None.
        """
        # Base case: If assignment is full, then all variables are accounted for.
        # We assume that if var is in assignment, there is a valid value.
        # Can also use assignment_complete function, but since all variables and values are guaranteed
        # to be valid when base case is reached, assignment_complete is redundant and adds auxiliary time.
        if len(assignment) == len(self.domains):
            return assignment

        for var in self.domains:
            if var in assignment:
                continue

            for potential_word in self.domains[var]:
                assignment[var] = potential_word
                if self.consistent(assignment):
                    res = self.backtrack(assignment)
                # If res is a dictionary instead of none, then it means we reached the base case.
                    if res:
                        return res
                # Backtracking.
                del assignment[var]


def main():

    # Check usage
    if len(sys.argv) not in [3, 4]:
        sys.exit("Usage: python generate.py structure words [output]")

    # Parse command-line arguments
    structure = sys.argv[1]
    words = sys.argv[2]
    output = sys.argv[3] if len(sys.argv) == 4 else None

    # Generate crossword
    crossword = Crossword(structure, words)
    creator = CrosswordCreator(crossword)
    assignment = creator.solve()

    # Print result
    if assignment is None:
        print("No solution.")
    else:
        creator.print(assignment)
        if output:
            creator.save(assignment, output)


if __name__ == "__main__":
    main()
