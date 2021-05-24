# Ball-Pivoting-Algorithm
Python implementation of the ball-pivoting algorithm (BPA), which was published in 1999 by Bernardini [1]. Some ideas in
this implementation were inspired by the implementation of Digne, which was published in 2014 [2].


## Algorithm Overview
This algorithm solves the problem of reconstructing mesh surface from a 3D point cloud. The main assumption this algorithm is
based on is the following: Given three vertices, and a ball of radius `r`, the three vertices form a triangle if the ball is getting "caught" and settle 
between the points, without containing any other point.

The algorithm stimulates a virtual ball of radius `r`. Each iteration consists of two steps:
- **Seed triangle** - The ball rolls over the point cloud until it gets "caught" between three vertices and settles between in them. 
Choosing the right `r` promises no other point is contained in the formed triangle. This triangle is called "Seed triangle".
- **Expanding triangle** - The ball pivots from each edge in the seed triangle, looking for a third point. It pivots until it gets
"caught" in the triangle formed by the edge and the third point. A new triangle is formed, and the algorithm
tries to expand from it. This process continues until the ball can't find any point to expand to.
  
At this point, the algorithm looks for a new seed triangle, and the process described above starts all over.

The following figures demonstrates those two steps. **Add figures**

Two vague assumptions that are necessary for the algorithm are that the point cloud is "dense enough", and that the
chosen `r` size is "slightly" larger than the average space between points. I couldn't find a metric method to evaluate
those two variables at the moment, and more work needs to be done on this.
  

## Data Structures
### Grid
I used a virtual 3D grid in which in each cell of the grid, all points are at distance of maximum `2r` from all 
other points. With this method, i am able to limit the number of points i need to search. Since we are looking to fit a
ball of radius `r` between three points, we can be assured that if the distance be two points is larger than `2r`, the ball
won't get caught between them. Therefore, while checking all possible points to pivot from a point `p` when generating 
seed triangle or expanding triangle, i need to check `p`'s cell, and all 8 cells that touches this cell. Example for that
is shown in the following figure. **Add figure**.

### 

## Implementation 

## Multithreading
I used multithreading in order to achieve 

## Complexity

## Visualizer
normal visualization.

## Dataset
source, and conversation from obj to txt.

## How to Run

## Examples

## Known Issues & TODOs
- overlapping
- "hole filling"
- choosing the right radius
- pre-checking if the point cloud is "dense enough"
- find a metric to evaluate how well the constructed mesh is.
- cuda support

## References
[1] [The Ball-Pivoting Algorithm for Surface Reconstruction](https://ieeexplore.ieee.org/stamp/stamp.jsp?tp=&arnumber=817351), by F. Bernardini, J. Mittleman and H. Rushmeier, 1999.

[2] [An Analysis and Implementation of a Parallel Ball Pivoting
Algorithm](https://www.ipol.im/pub/art/2014/81/article.pdf), by J. Digne, 2014.