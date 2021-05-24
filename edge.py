class Edge:
    def __init__(self, p1, p2):
        self.p1 = p1
        self.p2 = p2
        self.num_triangles_this_edge_is_in = 0 # To avoid cases where algorithm tries to expand edges that are already
        # part of 2 different triangles.
        self.color = [] # For visualization
