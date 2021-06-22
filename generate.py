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
                        w, h = draw.textsize(letters[i][j], font=font)
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
            wordsToRemove = []
            for word in self.domains[var]:
                if len(word) != var.length:
                    wordsToRemove.append(word)
            for word in wordsToRemove:
                self.domains[var].remove(word)

    def revise(self, x, y):
        """
        Make variable `x` arc consistent with variable `y`.
        To do so, remove values from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains[y]`.

        Return True if a revision was made to the domain of `x`; return
        False if no revision was made.
        """
        # Assign variables
        revision = False
        wordsX = self.domains[x]
        wordsY = self.domains[y]

        # Check if variable x has overlaps with y
        overlap = self.crossword.overlaps[x, y]

        # If no overlap was found, do nothing
        if overlap == None:
            pass
        
        # Else remove not compatible words from x
        else:

            # loop through all words of var x and for each
            wordsToRemove = []
            for wordX in wordsX:

                # Check if a compatible word exists in y domain (the overlap coincides)
                wordXpossible = False
                for wordY in wordsY:
                    if wordX[overlap[0]] == wordY[overlap[1]]:
                        wordXpossible = True
                
                # If the word of x domain is not possible, remove it
                if wordXpossible == False:
                    wordsToRemove.append(wordX)
                    revision = True

            for word in wordsToRemove:
                wordsX.remove(word)

        return revision


    def ac3(self, arcs=None):
        """
        Update `self.domains` such that each variable is arc consistent.
        If `arcs` is None, begin with initial list of all arcs in the problem.
        Otherwise, use `arcs` as the initial list of arcs to make consistent.

        Return True if arc consistency is enforced and no domains are empty;
        return False if one or more domains end up empty.
        """
        if arcs == None:
            arcs = []

            # Create a queue (list) of all arcs, i.e. overlaping variables
            for x in self.domains:
                for y in self.domains:
                    if x != y and self.crossword.overlaps[x, y] != None:
                        arcs.append((x,y))

        for arc in arcs:
            x = arc[0]
            y = arc[1]
            revision = self.revise(x, y)
            if revision == True:
                if len(self.domains[x]) == 0:
                    return False
                for neighbor in self.crossword.neighbors(x):
                    arcs.append((neighbor, x))

        return True

    def assignment_complete(self, assignment):
        """
        Return True if `assignment` is complete (i.e., assigns a value to each
        crossword variable); return False otherwise.
        """
        for var in self.domains:
            if var in assignment:
                continue
            else:
                return False
        return True

    def consistent(self, assignment):
        """
        Return True if `assignment` is consistent (i.e., words fit in crossword
        puzzle without conflicting characters); return False otherwise.
        """
        # First, check that all values in assignment are different
        for var1 in assignment:
            assignment2 = assignment.copy()
            assignment2.pop(var1)
            for var2 in assignment2:
                if var1 == var2:
                    return False

        # Second, check if all values in assignment have correct length
        for var in assignment:
            if var.length != len(assignment[var]):
                return False
        
        # Last, check there are no conflicts between neighboring variables
        for var in assignment:
            neighbors = self.crossword.neighbors(var)
            for neighbor in neighbors:
                overlap = self.crossword.overlaps[var, neighbor]
                if neighbor in assignment:
                    if assignment[var][overlap[0]] != assignment[neighbor][overlap[1]]:
                        return False
        
        return True

    def order_domain_values(self, var, assignment):
        """
        Return a list of values in the domain of `var`, in order by
        the number of values they rule out for neighboring variables.
        The first value in the list, for example, should be the one
        that rules out the fewest values among the neighbors of `var`.
        """
        list = []

        # Iterate through each word in domain of var
        for wordX in self.domains[var]:
            n = 0

            # Find for each neighbor of var
            for neighbor in self.crossword.neighbors(var):

                # Make sure it is not yet in assignment
                if neighbor not in assignment:

                    # Its overlaps with var
                    overlap = self.crossword.overlaps[var, neighbor]

                    # And for each value of neighbor, if the overlap is compatible.
                    for wordY in self.domains[neighbor]:

                        # n adds 1 if that value is ruled out for that word in var
                        if wordX[overlap[0]] != wordY[overlap[1]]:
                            n += 1
            
            # Create a tuple list with each word and its n value
            list.append((wordX, n))

        # Order the list according to n
        sortedList = sorted(list, key=lambda word: word[1])

        # Extract just the word list
        finalList = []
        for item in sortedList:
            finalList.append(item[0])

        return finalList

    def select_unassigned_variable(self, assignment):
        """
        Return an unassigned variable not already part of `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.
        """
        # Create a list of tuples of variables left and their number of remaining values
        listVarsN = []
        for var in self.domains:
            if var not in assignment:
                listVarsN.append((var, len(self.domains[var])))

        # Sort the list by ascencing order of remaining values left in its domain
        listVarsN_sorted = sorted(listVarsN, key=lambda var: var[1])
        
        # If there is a tie with the first, add all tie elements to a new list
        winners = []
        lenFirstVar = listVarsN_sorted[0][1]
        for item in listVarsN_sorted:
            if item[1] == lenFirstVar:
                winners.append(item[0])
            else:
                break

        # If the winners are more than 1, sort them by descencing degree
        if len(winners) > 1:
            listVarsD = []
            for var in winners:
                listVarsD.append((var, len(self.crossword.neighbors(var))))
            listVarsD_sorted = sorted(listVarsD, key=lambda var: var[1], reverse=True)
            return listVarsD_sorted[0][0]
        else:
            return winners[0]

    def backtrack(self, assignment):
        """
        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible to do so.

        `assignment` is a mapping from variables (keys) to words (values).

        If no assignment is possible, return None.
        """
        # If assignment is already complete, return assignment
        if self.assignment_complete(assignment):
            return assignment

        # Get an unassigned variable from assignment and loop through word domain
        var = self.select_unassigned_variable(assignment)
        for word in self.order_domain_values(var, assignment):

            # For each word, check consistency in an assignment dict copy with that word assigned to var
            testAssignment = assignment.copy()
            testAssignment[var] = word
            if self.consistent(testAssignment):

                # If the word creates a consistent assignment, recursively call backtrack to continue assigning
                result = self.backtrack(testAssignment)

                # If the CSP was solved, the last recursive return will be an assignment, which we return recursively
                if result != None:
                    return result

        # If no solution is found, return None
        return None


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
