# 3SAT Solver Using Vector Math and Numpy
Sep 22nd, 2026 \
Jaden Wang

### Processing the data
So for this, I decided to turn 3SAT into an algebraic problem using vectors and matrices, since this woudl allow me to solve it algebracally too. I envisioned each clause of the 3SAT expression as an (n x 3) matrix, which would be applied to a shared input vector. So, overall, the full configuration is an (m x n x 3) tensor that contain all of the clauses.

The matrices are filled with 0s, 1s, and -1s, with 1s signifying that a variable is in the clause and -1s signifing that the variable is in the clause and has a NOT gate in front of it. The inputs consist of 1s and -1s to represent True and False respectively. I chose to use 1s and -1s to signify both True/False and identity/NOT-gates because they are easy to manipulate algebrically. 

Then, the matrix would be transformed element-wise to map 1s to 0 and -1s to 1. This allows me to perform a horizontal multiplication that perfect simulates or gates, as a single 0 would set the clause equal to 0, whice is a transformed representation of True. 

Now, we have a column vector since the matrix was shrunk horizontally. Applying one more transformation maps 1 to 0 and 0 to 1. This means 1 represents True now, and 0 represents False. We wan this becasue now, by multiplying vertically, we can represent a collection of AND gates vertically.

Now, finally, we have our output, which returns 1 is the original 3SAT expression evaluates to True and 0 if it evaluates to False. 

### Tracing it back
Now, time to trace the expression back to see what inputs satisfy the system in terms of the configuration tensor T. In order for the output to be True, the penultimate vector must all be 1s, because AND gates only evaluate to True if all of the Terms are True.

Going back a step, there is a product (the horizontal product), which drastically increases the number of valid configurations, since any permuation of three terms that contain a single True (represented by 0 in this case) will evaluate to True in the column vector. There are 7 of these possible vectors.

Now, we once again transform our numbers ot a realm where 1 represents True and -1 represents False. There are still seven options for each row of this matrix  and each of them yield different information about the input vector when passed backwards through a layer of T (by transposing the layer of T and calculating the dot product).

My first though here was to take a layer of T, check each of these 7 combinations, flag them as possible, and move on to the next layer to obtain more information. However, I then realized I could just rule out the case where all three terms are False (the [-1, -1, -1]) vector for every layer of T, then check if we have any solutions left. 

By assuming that all solutions work initially, I could filter down the range of possible solutions using each layer of T (or clause in the 3SAT expression). Seeing this, I quickly developed a code solution to test my method out.

### Implementing it in code
