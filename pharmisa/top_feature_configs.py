from itertools import combinations


def get_number_of_configs(spheres_list: list):
    """Number of configs"""
    if len(spheres_list) > 5:
        number_configs = 3
    else:
        configs = len(spheres_list) - 3
        if configs == 0:
            number_configs = 1
        else:
            number_configs = configs + 1
    return number_configs


def get_all_combinations_with_n(spheres_list: list, n: int):
    """All combinations from spheres list with n elements"""
    all_n_combinations = list(combinations(spheres_list, n))
    valid_combinations = []

    for combination in all_n_combinations:
        coordinates = [(sphere.x, sphere.y, sphere.z) for sphere in combination]
        if len(coordinates) == len(set(coordinates)):  # check if all coordinates are unique
            valid_combinations.append(combination)

    return valid_combinations


def max_quantity_tuple(combinations_list: list):
    """Get the combination with the max quantity"""
    max_tuple = ()
    max_quantity = 0
    for comb_tuple in combinations_list:
        tuple_sum = sum(sphere.quantity_matched for sphere in comb_tuple)
        if tuple_sum > max_quantity:
            max_quantity = tuple_sum
            max_tuple = comb_tuple

    return max_tuple


def run_feature_configs(spheres_list: list):
    """Run the feature configs"""
    number_configs = get_number_of_configs(spheres_list)
    all_combinations = []
    final_combinations = []
    for index, n in enumerate(range(number_configs)):
        n = index + 3
        all_combinations.append(get_all_combinations_with_n(spheres_list, n))
    for combinations_list in all_combinations:
        max_tuple = max_quantity_tuple(combinations_list)
        final_combinations.append(max_tuple)

    return final_combinations
