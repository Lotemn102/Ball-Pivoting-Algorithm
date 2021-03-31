x = 1
y = 1
z = 1

l = []

for i in range(-1, 2):
    for j in range(-1, 2):
        for k in range(-1, 2):
            p = x + i, y + j, z + k
            l.append(p)

print(len(l))