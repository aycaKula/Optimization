from itertools import product
from sys import stdout as out
from mip import Model, xsum, minimize, BINARY

# names of places to visit
places = ['Antwerp', 'Bruges', 'C-Mine', 'Dinant', 'Ghent',
'Grand-Place de Bruxelles', 'Hasselt', 'Leuven',
'Mechelen', 'Mons', 'Montagne de Bueren', 'Namur',
'Remouchamps', 'Waterloo']

# distances in an upper triangular matrix
dists = [[83, 81, 113, 52, 42, 73, 44, 23, 91, 105, 90, 124, 57],
[161, 160, 39, 89, 151, 110, 90, 99, 177, 143, 193, 100],
[90, 125, 82, 13, 57, 71, 123, 38, 72, 59, 82],
[123, 77, 81, 71, 91, 72, 64, 24, 62, 63],
[51, 114, 72, 54, 69, 139, 105, 155, 62],
[70, 25, 22, 52, 90, 56, 105, 16],
[45, 61, 111, 36, 61, 57, 70],
[23, 71, 67, 48, 85, 29],
[74, 89, 69, 107, 36],
[117, 65, 125, 43],
[54, 22, 84],
[60, 44],
[97],
[]]

# number of nodes and list of vertices
n, V = len(dists), set(range(len(dists)))

# distances matrix
c = [[0 if i == j
        else dists[i][j-i-1]
        if j > i else dists[j][i-j-1]
        for j in V] for i in V]

print(c)


try_

model = Model()



