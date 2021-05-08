# Ball-Pivoting-Algorithm
Python implementation of the Ball-Pivoting algorithm (BPA).

## Ideas

- Encoding each cell in the grid into unique integer based on a single corner. Using hash table
where keys are these code-words and the data are the points contained in this cell.
We can go through all data and find the bounding box of the whole data set. Given specific `r` we can
calculate each cell corners (since each cell size is `2r`). We are only adding to the has table
cells that contains actual points.  
  
  
## Papers
http://jbehley.github.io/papers/behley2015icra.pdf

https://www.ipol.im/pub/art/2014/81/article.pdf

http://www.sci.utah.edu/~csilva/papers/tvcg99.pdf

## TODO
- ~~Check if we can easily add edges to point in the point cloud using Open3d.~~
- Fix the overlapping triangles - If a point is the same direction as if the third point in the triangle we expand, don't take it!
- "Circle triangulation" update the number of the triangles the last edge is in.

