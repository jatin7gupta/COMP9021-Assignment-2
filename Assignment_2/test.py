from collections import namedtuple

Point = namedtuple('Point', 'x y')

def rotate(list_of_points):
    for _ in range(len(list_of_points)+1):
        last_point = list_of_points.pop(0)
        list_of_points.append(last_point)
        print(list_of_points)
    pass


print(rotate(['A', 'B', 'C', 'D']))
lst = ['A', 'B', 'C', 'D']
print(lst[::-1])