import xml.etree.ElementTree as ET
import re
from collections import namedtuple
import numpy as np
import itertools as it
from operator import xor
import math

Point = namedtuple('Point', 'x y')
# file1 = open('not-valid-no-pieces.xml')
# file2 = open('tangram_A_2_a.xml')


def available_coloured_pieces(f):
    # will return something that has all the pieces
    tree = ET.parse(f)
    root = tree.getroot()
    i = 0
    coordinates_list = []
    color_list = []
    for child in root:
        for key, val in child.items():
            if i % 2 == 0:
                coordinates_list.append(val)
            else:
                color_list.append(val)
            i += 1

    def give_coordinates_from_string(s):
        return_list = []
        list_of_matches = re.findall('\\d+\\s\\d+', s)
        for match in list_of_matches:
            list_numbers = re.findall('\\d+', match)
            return_list.append(Point(int(list_numbers[0]), int(list_numbers[1])))
        return return_list

    list_of_coordinates = []
    for e in coordinates_list:
        list_of_coordinates.append(give_coordinates_from_string(e))

    dict_color_coordinates = {}
    for i in range(len(list_of_coordinates)):
        dict_color_coordinates[color_list[i]] = list_of_coordinates[i]

    return dict_color_coordinates


def make_matrix(list_of_three_points):
    matrix = []
    for point in list_of_three_points:
        matrix.append([1] + [point.x] + [point.y])
    return matrix


def check_orientation_of_vectors(list_of_three_points):
    matrix = make_matrix(list_of_three_points)
    det = np.linalg.det(matrix)
    if det == 0:
        return None
    if det < 0:
        return False
    if det > 0:
        return True


def check_convex(list_of_points):
    list_of_points_to_function = []
    result_of_orientation = None
    for i in range(len(list_of_points)):
        list_of_points_to_function.append(list_of_points[i])
        if i+1 < len(list_of_points) and i+2 < len(list_of_points):
            list_of_points_to_function.append(list_of_points[i+1])
            list_of_points_to_function.append(list_of_points[i+2])
            result = check_orientation_of_vectors(list_of_points_to_function.copy())
            if result is None:
                # det = 0
                return False
            if result_of_orientation is None:
                result_of_orientation = result
            if result != result_of_orientation:
                return False

        list_of_points_to_function.clear()
    last_two_points = list_of_points[-2:]
    first_point = list_of_points[0]
    last_two_points.append(first_point)
    result_last_two_and_first = check_orientation_of_vectors(last_two_points)

    last_point = list_of_points[-1]
    first_two = list_of_points[:2]
    first_two.insert(0, last_point)
    result_last_and_first_two = check_orientation_of_vectors(first_two)

    if result_last_two_and_first is None or result_last_and_first_two is None:
        # det = 0
        return False
    if result_last_and_first_two != result_of_orientation or result_last_two_and_first != result_of_orientation :
        return False

    return True
    # returns true or false


def check_four_points_intersecting(p1, p2, p3, p4):
    det_p1_p2_p3 = check_orientation_of_vectors([p1, p2, p3])
    det_p1_p2_p4 = check_orientation_of_vectors([p1, p2, p4])
    if det_p1_p2_p3 is None or det_p1_p2_p4 is None:
        return True
    if xor(det_p1_p2_p3, det_p1_p2_p4):
        det_p3_p4_p1 = check_orientation_of_vectors([p3, p4, p1])
        det_p3_p4_p2 = check_orientation_of_vectors([p3, p4, p2])
        if det_p3_p4_p1 is None or det_p3_p4_p2 is None:
            return True
        if xor(det_p3_p4_p1, det_p3_p4_p2):
            return True
    return False


def intersecting(list_of_points):
    for p1 in range(len(list_of_points)):
        if p1 + 4 <= len(list_of_points):
            p2 = p1 + 1
            for p3 in range(p2+1, len(list_of_points)-1):
                p4 = p3 + 1
                if check_four_points_intersecting(
                    list_of_points[p1],
                    list_of_points[p2],
                    list_of_points[p3],
                    list_of_points[p4]
                     ):
                    return True
    p1 = list_of_points[-3]
    p2 = list_of_points[-2]
    p3 = list_of_points[-1]
    p4 = list_of_points[0]
    if check_four_points_intersecting(p1, p2, p3, p4):
        return True
    p5 = list_of_points[1]
    p6 = list_of_points[2]
    if check_four_points_intersecting(p3, p4, p5, p6):
        return True

    return False


def are_valid(coloured_pieces):
    if len(coloured_pieces) >= 1:
        for list_of_points in coloured_pieces.values():
            if len(list_of_points) >= 3:
                if not check_convex(list_of_points):
                    return False
                if len(list_of_points) >= 4:
                    if intersecting(list_of_points):
                        return False
            else:
                return False
        return True
    else:
        return False


def translate(list_of_points):
    # translate by finding min of x and y and subtracting it from all points
    return_list = []
    min_x = list_of_points[0].x
    min_y = list_of_points[0].y
    for point in list_of_points:
        if min_x > point.x:
            min_x = point.x
        if min_y > point.y:
            min_y = point.y
    for point in list_of_points:
        return_list.append(Point(point.x - min_x, point.y - min_y))
    return return_list


def make_eight_copies(list_of_points):
    result_list = []   # translate(list_of_points)
    result_list.append(translate(list_of_points))

    # mirror y axis
    mirror_y_axis = []
    for point in list_of_points:
        mirror_y_axis.append(Point(-point.x, point.y))
    result_list.append(translate(mirror_y_axis))

    # mirror x axis
    mirror_x_axis = []
    for point in list_of_points:
        mirror_x_axis.append(Point(point.x, -point.y))
    result_list.append(translate(mirror_x_axis))

    # mirror x and y axis
    mirror_x_y_axis = []
    for point in list_of_points:
        mirror_x_y_axis.append(Point(-point.x, -point.y))
    result_list.append(translate(mirror_x_y_axis))

    # transform x and y
    transform_x_y = []
    for point in list_of_points:
        transform_x_y.append(Point(point.y, point.x))
    result_list.append(translate(transform_x_y))

    # transform mirror y axis
    transform_x_y_mirror_y_axis = []
    for point in list_of_points:
        transform_x_y_mirror_y_axis.append(Point(-point.y, point.x))
    result_list.append(translate(transform_x_y_mirror_y_axis))

    # transform mirror x axis
    transform_x_y_mirror_x_axis = []
    for point in list_of_points:
        transform_x_y_mirror_x_axis.append(Point(point.y, -point.x))
    result_list.append(translate(transform_x_y_mirror_x_axis))

    # transform mirror x and y axis
    transform_x_y_mirror_x_y_axis = []
    for point in list_of_points:
        transform_x_y_mirror_x_y_axis.append(Point(-point.y, -point.x))
    result_list.append(translate(transform_x_y_mirror_x_y_axis))

    return result_list


# def check_by_rotating_anti_clockwise(piece_1, piece_2):
#     if piece_1 == piece_2:
#         return True
#     if piece_1 == piece_2[::-1]:
#         return True
#     for _ in range(len(piece_2)):
#         last_point = piece_2.pop(-1)
#         piece_2.insert(0, last_point)
#         if piece_1 == piece_2:
#             return True
#     return False


def check_by_rotating_clockwise(piece_1, piece_2):
    if piece_1 == piece_2:
        return True

    for _ in range(len(piece_2)):
        first_point = piece_2.pop(0)
        piece_2.append(first_point)
        if piece_1 == piece_2:
            return True
    return False


def check_by_matching(piece_1, piece_2):
    if not check_by_rotating_clockwise(piece_1, piece_2):
        if not check_by_rotating_clockwise(piece_1, piece_2[::-1]):
            return False
        else:
            return True
    else:
        return True


def check_identical_from_eight_potential_options(coloured_piece_1, coloured_piece_2_potential_list):
    for piece_2 in coloured_piece_2_potential_list:
        if check_by_matching(coloured_piece_1, piece_2):
            return True
    return False


def are_identical_sets_of_coloured_pieces(coloured_pieces_1, coloured_pieces_2):
    # todo can pieces have no points?
    if coloured_pieces_1.keys() == coloured_pieces_2.keys() \
            and are_valid(coloured_pieces_1) and are_valid(coloured_pieces_2):
        for key_1, list_of_points_1 in coloured_pieces_1.items():
            for key_2, list_of_points_2 in coloured_pieces_2.items():
                if key_1 == key_2:
                    if len(coloured_pieces_1[key_1]) == len(coloured_pieces_2[key_2]):
                        translated_coloured_pieces_1_points = translate(coloured_pieces_1[key_1])
                        translated_coloured_pieces_2_eight_lists = make_eight_copies(coloured_pieces_2[key_2])
                        if check_identical_from_eight_potential_options(
                                translated_coloured_pieces_1_points,
                                translated_coloured_pieces_2_eight_lists):
                            pass
                        else:
                            return False
                    else:
                        return False
        return True
    else:
        return False


def area(list_of_points):
    list_x = []
    list_y = []
    for point in list_of_points:
        list_x.append(point.x)
        list_y.append(point.y)
    n = len(list_of_points)
    area = 0.0
    j = n - 1
    for i in range(0, n):
        area += (list_x[j] + list_x[i]) * (list_y[j] - list_y[i])
        j = i  # j is previous vertex to i

    return abs(area / 2.0)


def check_all_points_inside_shape(tangram, shape):
    # find max and min of shape
    max_x_shape = -math.inf
    max_y_shape = -math.inf
    min_x_shape = math.inf
    min_y_shape = math.inf
    for values in shape.values():
        for point in values:
            if max_x_shape <= point.x:
                max_x_shape = point.x
            if max_y_shape <= point.y:
                max_y_shape = point.y
            if min_x_shape >= point.x:
                min_x_shape = point.x
            if min_y_shape >= point.y:
                min_y_shape = point.y
    for list_of_points in tangram.values():
        for point in list_of_points:
            if point.x > max_x_shape or point.x < min_x_shape or point.y > max_y_shape or point.y < min_y_shape:
                return False
    return True


def check_four_points_intersecting_part_three(p1, p2, p3, p4):
    # true means p1 p2 intersects with p3 p4
    # false means p1 p2 does not intersects with p3 p4
    # check orientation function can return None as well when they are co linear
    # Todo confirm with Dhan or atul
    det_p1_p2_p3 = check_orientation_of_vectors([p1, p2, p3])
    det_p1_p2_p4 = check_orientation_of_vectors([p1, p2, p4])
    if det_p1_p2_p3 is None or det_p1_p2_p4 is None:
        return False
    if xor(det_p1_p2_p3, det_p1_p2_p4):
        det_p3_p4_p1 = check_orientation_of_vectors([p3, p4, p1])
        det_p3_p4_p2 = check_orientation_of_vectors([p3, p4, p2])
        if det_p3_p4_p1 is None or det_p3_p4_p2 is None:
            return False
        if xor(det_p3_p4_p1, det_p3_p4_p2):
            return True
    return False


def on_line(p1, p2, p3):
    if min(p1.x, p2.x) <= p3.x <= max(p1.x, p2.x) and p3.x:
        if min(p1.y, p2.y) <= p3.y <= max(p1.y, p2.y) and p3.y:
            return True
    return False


def check_four_points_intersecting_part_three_ray(p1, p2, p3, p4):
    det_p1_p2_p3 = check_orientation_of_vectors([p1, p2, p3])
    det_p1_p2_p4 = check_orientation_of_vectors([p1, p2, p4])
    det_p3_p4_p1 = check_orientation_of_vectors([p3, p4, p1])
    det_p3_p4_p2 = check_orientation_of_vectors([p3, p4, p2])
    if det_p1_p2_p3 is not None and det_p1_p2_p4 is not None and det_p3_p4_p1 is not None and det_p3_p4_p2 is not None:
        if xor(det_p1_p2_p3, det_p1_p2_p4):
            if xor(det_p3_p4_p1, det_p3_p4_p2):
                return True
    elif det_p1_p2_p3 is None and not on_line(p1, p2, p3):
        return True
    elif det_p1_p2_p4 is None and not on_line(p1, p2, p4):
        return True
    elif det_p3_p4_p1 is None and not on_line(p3, p4, p1):
        return True
    elif det_p3_p4_p2 is None and not on_line(p3, p4, p2):
        return True
    return False


def intersect(list_of_points_shape, p3, p4):
    for i in range(len(list_of_points_shape)):
        if i + 1 < len(list_of_points_shape):
            p1 = list_of_points_shape[i]
            p2 = list_of_points_shape[i + 1]
            if check_four_points_intersecting_part_three(p1, p2, p3, p4):
                return True
    last_point = list_of_points_shape[-1]
    first_point = list_of_points_shape[0]
    if check_four_points_intersecting_part_three(last_point, first_point, p3, p4):
        return True
    return False


def check_intersection_shape_tangram(tangram, shape):
    list_of_points_shape = []
    for value_of_shape in shape.values():
        list_of_points_shape = value_of_shape

    for list_of_points_tangram in tangram.values():
        for p in range(len(list_of_points_tangram)):
            if p+1 < len(list_of_points_tangram):
                p3 = list_of_points_tangram[p]
                p4 = list_of_points_tangram[p+1]
                if intersect(list_of_points_shape, p3, p4):
                    return True
        last_point = list_of_points_tangram[-1]
        first_point = list_of_points_tangram[0]
        if intersect(list_of_points_shape, last_point, first_point):
            return True
    return False


def check_intersection_between_point_piece2(piece2, p1, p2):
    for point_of_piece_2 in range(len(piece2)):
        if point_of_piece_2 + 1 < len(piece2):
            p3 = piece2[point_of_piece_2]
            p4 = piece2[point_of_piece_2 + 1]
            if check_four_points_intersecting_part_three(p1, p2, p3, p4):
                return True
    last_point = piece2[-1]
    first_point = piece2[0]
    if check_four_points_intersecting_part_three(p1, p2, last_point, first_point):
        return True
    return False


def check_intersection_between_pieces(piece1, piece2):
    for point_of_piece_1 in range(len(piece1)):
        if point_of_piece_1 + 1 < len(piece1):
            p1 = piece1[point_of_piece_1]
            p2 = piece1[point_of_piece_1 + 1]
            if check_intersection_between_point_piece2(piece2, p1, p2):
                return True
    last_point = piece1[-1]
    first_point = piece1[0]
    if check_intersection_between_point_piece2(piece2, last_point, first_point):
        return True
    return False


def check_intersection_pieces_tangram(tangram):
    list_of_list_of_points = []
    for list_of_points in tangram.values():
        list_of_list_of_points.append(list_of_points)

    for l in range(len(list_of_list_of_points)):
        if l+1 < len(list_of_list_of_points):
            if check_intersection_between_pieces(list_of_list_of_points[l], list_of_list_of_points[l+1]):
                return True
    last_list = list_of_list_of_points[-1]
    first_list = list_of_list_of_points[0]
    if check_intersection_between_pieces(last_list, first_list):
        return True
    return False


def is_solution(tangram, shape):
    # tangram has multiple pieces
    # shape has only one piece
    list_of_points_shape = []
    for key, value in shape.items():
        list_of_points_shape = value
    area_of_shape = area(list_of_points_shape)
    area_of_tangram_pieces = 0.0
    for key, value in tangram.items():
        area_of_tangram_pieces += area(tangram[key])
    if area_of_shape == area_of_tangram_pieces \
            and check_all_points_inside_shape(tangram, shape) \
            and not check_intersection_pieces_tangram(tangram) \
            and not check_intersection_shape_tangram(tangram, shape):
        return True
        # proceed with other checks
    return False


# shape = available_coloured_pieces(file1)
# tangram = available_coloured_pieces(file2)
# print(are_valid(shape))
