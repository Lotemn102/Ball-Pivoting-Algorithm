# Ball-Pivoting-Algorithm
Python implementation of the Ball-Pivoting algorithm (BPA).

This algorithm was introduced by Bernardini in his paper [The BalI-Pivoting
Algorithm for Surface Reconstruction](http://www.sci.utah.edu/~csilva/papers/tvcg99.pdf). I've used in my
implementation ideas from Digne's paper [An Analysis and Implementation of a Parallel Ball Pivoting
Algorithm](https://www.ipol.im/pub/art/2014/81/article.pdf), and Behley's, Steinhage's, and Cremers' paper  
[Efficient Radius Neighbor Search in Three-dimensional Point Clouds](http://jbehley.github.io/papers/behley2015icra.pdf).

## Ball Pivoting Algorithm

## Data Structures
The data structure used in this implementation is an octree, where each node contains references to all points
contained in it's sub-tree. 

## Fixed Radius Near Neighbor Algorithm
Digne suggests to use an octree where the leaves' cell size is bounded by the parameter `r`. 
This way when looking for new points in the `r`-neighborhood of a point `p`, you only have to check the 8 neighbor cells
to `p`'s cell. She also presented efficient method to achieve those neighbors cells in constant time. However, this approach isn't suitable for dynamically changes in radius size, since one would have to re-construct
the whole octree in order to do so in every radius change.

Instead, i've used in my implementation Behley's, Steinhage's, and Cremers' approach.
In their paper [Efficient Radius Neighbor Search in Three-dimensional Point Clouds](http://jbehley.github.io/papers/behley2015icra.pdf)
they suggest the following method to search for all points in the neighborhood of radius of `r` from a given point `p`:
- Create a linked list contains all points in the data set. While constructing the octree, connect by reference each
node in the tree with all the points contained in it's sub-tree.
- Starting from the root of the octree, traverse the tree and at each node, check if it's contained in the sphere `S(p, r)`.
If it is contained, add all points contained in the that node the neighborhood and return. Else, keep traversing.

Thanks to that pruning, they managed to decrease the running time of the algorithm, compared to other method without pruning.
Check out the paper for extra details.


## Papers
http://jbehley.github.io/papers/behley2015icra.pdf

https://www.ipol.im/pub/art/2014/81/article.pdf

http://www.sci.utah.edu/~csilva/papers/tvcg99.pdf

