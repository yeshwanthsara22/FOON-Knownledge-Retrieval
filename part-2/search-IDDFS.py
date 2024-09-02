import pickle
import json
from FOON_class import Object

# -----------------------------------------------------------------------------------------------------------------------------#

# Checks an ingredient exists in kitchen


def check_if_exist_in_kitchen(kitchen_items, ingredient):
    """
        parameters: a list of all kitchen items,
                    an ingredient to be searched in the kitchen
        returns: True if ingredient exists in the kitchen
    """

    for item in kitchen_items:
        if item["label"] == ingredient.label \
                and sorted(item["states"]) == sorted(ingredient.states) \
                and sorted(item["ingredients"]) == sorted(ingredient.ingredients) \
                and item["container"] == ingredient.container:
            return True

    return False


# -----------------------------------------------------------------------------------------------------------------------------#

def save_paths_to_file(task_tree, path):

    print('writing generated task tree to ', path)
    _file = open(path, 'w')

    _file.write('//\n')
    for FU in task_tree:
        _file.write(FU.get_FU_as_text() + "\n")
    _file.close()

def is_valid_input(target_node, candidate_node_index):
    if target_node.label in utensils or len(target_node.ingredients) != 1:
        return True
    
    for node in foon_functional_units[
            candidate_node_index].input_nodes:
        if node.label == target_node.ingredients[
                0] and node.container == target_node.label:

            return False
    return True


def search_iterative_deepening_search(kitchen_items=[], goal_node=None, depth_limit=10):
    
    def depth_limited_search(current_item, kitchen_items, current_depth, max_depth):
        if check_if_exist_in_kitchen(kitchen_items, current_item) :
            return 'continue'

        # Explore children nodes
        if current_item.id not in foon_object_to_FU_map:
            return [current_item.id]

        if(current_depth >= max_depth):
            return []
        candidate_units = foon_object_to_FU_map[current_item.id]


        optimal_candidate_index = candidate_units[0]
        path_so_far = []
        for node in foon_functional_units[optimal_candidate_index].input_nodes:
            if is_valid_input(node, optimal_candidate_index):
                path = depth_limited_search(node, kitchen_items, current_depth + 1, max_depth)
                if path == 'continue':
                    continue
                elif path != [] :
                    path_so_far += path

                else:
                    path_so_far = []
                    break

        return path_so_far + [optimal_candidate_index]

    # Iteratively increasing depth for depth_limited_search
    for i in range(0, depth_limit + 1):
        result = depth_limited_search(goal_node, kitchen_items, 0, i)
        if result != []:
            return [foon_functional_units[i] for i in result] 
    return None



# -----------------------------------------------------------------------------------------------------------------------------#

# creates the graph using adjacency list
# each object has a list of functional list where it is an output


def read_universal_foon(filepath='FOON.pkl'):
    """
        parameters: path of universal foon (pickle file)
        returns: a map. key = object, value = list of functional units
    """
    pickle_data = pickle.load(open(filepath, 'rb'))
    functional_units = pickle_data["functional_units"]
    object_nodes = pickle_data["object_nodes"]
    object_to_FU_map = pickle_data["object_to_FU_map"]

    return functional_units, object_nodes, object_to_FU_map


# -----------------------------------------------------------------------------------------------------------------------------#

if __name__ == '__main__':
    foon_functional_units, foon_object_nodes, foon_object_to_FU_map = read_universal_foon(
    )

    utensils = []
    with open('utensils.txt', 'r') as f:
        for line in f:
            utensils.append(line.rstrip())

    kitchen_items = json.load(open('kitchen.json'))

    goal_nodes = json.load(open("goal_nodes.json"))

    for node in goal_nodes:
        node_object = Object(node["label"])
        node_object.states = node["states"]
        node_object.ingredients = node["ingredients"]
        node_object.container = node["container"]

        for object in foon_object_nodes:
            if object.check_object_equal(node_object):
                output_task_tree = search_iterative_deepening_search(kitchen_items, object)
                if output_task_tree is not None:
                    new_list = []
                    [new_list.append(item) for item in output_task_tree if item not in new_list]
                    save_paths_to_file(new_list, 'output/output_IDDFS_{}.txt'.format(node["label"]))
                else:
                    print("No path found for {}".format(node["label"]))
                break
