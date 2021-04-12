def create_without_normal():
    f = open("test_1_no_normal.txt", "w")

    points = []
    n = 3

    for i in range(0, n):
        for j in range(0, n):
            for k in range(0, n):
                if i == 0 or j == 0 or k == 0 or i == n - 1 or j == n - 1 or k == n - 1:
                    points.append((i + 1, j + 1, k + 1))

    f.close()

