f = open('../sample_w_normals.txt', "r")
output = open('clean.txt', 'w')
lines = f.read().splitlines()

for line in lines:
    coordinates = line.split()

    clean_line = coordinates[0] + " " + coordinates[1] + " " + coordinates[2] + " " + coordinates[6] + " " +\
                 coordinates[7] + " " + coordinates[8] + "\n"
    output.write(clean_line)

f.close()
output.close()

