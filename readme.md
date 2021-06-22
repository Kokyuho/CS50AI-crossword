# CS50’s Introduction to Artificial Intelligence with Python
# Project 3: Optimization: Crossword

**Aim**: Write an AI to generate crossword puzzles.

**Description**: In this problem we write a program able to find satisfying assignment of words for a crossword puzzle given a certain vocabulary list. We can model this type of problem as a contraint satisfaction problem, in which our algorithm must be able to find a solution which satisfies all given contrains, like in this case the length and crossing of each word, as well as not reapeating any words.

There are two Python files in this project:  
- crossword.py: This file defines two classes, Variable (to represent a variable in a crossword puzzle) and Crossword (to represent the puzzle itself).
- generate.py: Here, we define a class CrosswordCreator that we’ll use to solve the crossword puzzle.

See full problem description here: https://cs50.harvard.edu/ai/2020/projects/3/crossword/


Usage:
```
python generate.py structure words [output]
```

Example:
```
$ python generate.py data/structure1.txt data/words1.txt output.png
██████████████
███████M████R█
█INTELLIGENCE█
█N█████N████S█
█F██LOGIC███O█
█E█████M████L█
█R███SEARCH█V█
███████X████E█
██████████████
```
