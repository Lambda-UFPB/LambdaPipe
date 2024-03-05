from pharma_optimizer import PharmaOptimizer
from itertools import combinations
from json_handler import JsonHandler


def get_number_of_configs(spheres_list: list):
    """Number of configs"""
    configs = len(spheres_list) - 3
    if configs == 0:
        number_configs = 1
    else:
        number_configs = configs + 1
    return number_configs


def get_all_combinations_with_n(spheres_list: list, n: int):
    """All combinations from spheres list with n elements"""
    all_n_combinations = list(combinations(spheres_list, n))
    return all_n_combinations


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


if __name__ == '__main__':
    pharmit_json_path = '/home/kdunorat/Projetos/LambdaPipe/files/pharmit (3).json'
    plip_csv = '/home/kdunorat/Projetos/LambdaPipe/files/7KR1-pocket3-interact.csv'
    popt = PharmaOptimizer(pharmit_json_path, plip_csv)
    pharmit_spheres_list = popt.run_pharma_optimizer()
    configs_list = run_feature_configs(pharmit_spheres_list)

    """"""
    jsh = JsonHandler(output_file_path='/home/kdunorat/Projetos/LambdaPipe/files', pharmit_json=pharmit_json_path)
    jsh.write_points(configs_list)
    jsh.create_json()


