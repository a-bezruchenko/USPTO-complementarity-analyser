import os
import numpy as np
from time import time

status_filename = "analyser_status"

class cd:
    """Context manager for changing the current working directory"""
    def __init__(self, newPath):
        self.newPath = os.path.expanduser(newPath)
    def __enter__(self):
        self.savedPath = os.getcwd()
        os.chdir(self.newPath)
    def __exit__(self, etype, value, traceback):
        os.chdir(self.savedPath)

def get_patent_id(filename):
    return int(filename[filename.rfind('/')+1:])

def split_line(line):
    splitted = line.strip().split("\t")
    patent_id = get_patent_id(splitted[1])
    topics = [float(num) for num in splitted[2:]]
    return patent_id, topics

def apply_threshold(arr, threshold):
    return [0 if x < threshold else 1  for x in arr]

def filter_threshold(arr, threshold):
    return [i for i,x in enumerate(arr) if x >= threshold]

# filename = "doc_topics.txt"
# def get_patent_to_topic_matrix(filename):
#     with open(filename, "r") as f:
#         patent_to_topics = f.readlines()
#     splitted = [split_line(line) for line in patent_to_topics]
#     filtered = {id:filter_threshold(data, topic_threshold) for id, data in splitted}
#     return filtered

def get_patent_to_topic_matrix(filename):
    with open(filename, "r") as f:
        patent_to_topics = f.readlines()
    splitted = [line.strip().split("\t") for line in patent_to_topics]
    filtered = {int(patent):[int(topic)] for patent, topic in splitted}
    return filtered

def show_ones(x):
    if x == 0:
        return ' '
    else:
        return '*'

# def print_data(filtered):
#     for id, data in filtered:
#         print(f"{id:08d}|{''.join(list(map(show_ones,data)))}")

def get_files_in_directory(dir_name):
    names = [dir_name]
    i = 0
    while i < len(names):
        if os.path.isdir(names[i]):
            names += list(map(lambda x: f"{names[i]}/{x}", os.listdir(names[i])))
        i += 1
    return [name for name in names if os.path.isfile(name)]

def get_firms(firm_dir):
    filenames = get_files_in_directory(firm_dir)
    firms = dict()
    for filename in filenames:
        with open(filename, "r", encoding="utf-8") as f:
            for line in f:
                splitted = line.strip().split('\t')
                if len(splitted) != 1: # если равно 1, то фирм нет, игнорируем
                    for firm in splitted[1:]:
                        if firm in firms.keys():
                            firms[firm] += 1
                        else:
                            firms[firm] = 1
    return firms
    
def get_topic_tree(filename):
    result_tree = {}
    result_customers = {}
    result_children = {}
    with open(filename, "r", encoding="utf-8") as f:
        for line in f:
            splitted = line.strip().split('\t')
            if len(splitted) == 2:
                node, customers = splitted
                node, customers = int(node), int(customers)
                result_children[node] = []
            elif len(splitted) == 3:
                node, customers, parent = splitted
                node, customers, parent = int(node), int(customers), int(parent)
                result_tree[node] = parent
                if parent in result_children:
                    result_children[parent].append(node)
                else:
                    result_children[parent] = [node]
            result_customers[node] = customers
    return result_tree, result_customers, result_children

# def get_firm_to_topic_matrix(patent_to_topics_matrix, firm_dir, topic_tree):
#     firms = get_firms(firm_dir)
#     firms = [firm for firm in firms if firms[firm] > firm_patents_threshold]
#     firms = {firm:i for i, firm in enumerate(firms)}
#     topics_to_internal = {t:i for i,t in enumerate(topic_tree)}
#     topics_from_internal = {topics_to_internal[i]:i for i in topics_to_internal}
#     topics_count = len(topics_to_internal) + 1
#     result = np.zeros((len(firms), topics_count,))
#     filenames = get_files_in_directory(firm_dir)
#     for filename in filenames:
#         with open(filename, "r", encoding="utf-8") as f:
#             for line in f:
#                 splitted = line.strip().split('\t')
#                 if len(splitted) != 1: # если равно 1, то фирм нет, игнорируем
#                     patent_id = int(splitted[0])
#                     if patent_id not in patent_to_topics_matrix.keys():
#                         #print(f"can't find patent {patent_id}")
#                         pass
#                     else:
#                         for firm in splitted[1:]:
#                             if firm in firms.keys():
#                                 for topic in patent_to_topics_matrix[patent_id]:
#                                     result[firms[firm], topics_to_internal[topic]] += 1
#                             else:
#                                 #print(f"firm {firm} not in firms")
#                                 pass
#     return result, firms, topics_from_internal

def calc_firm_to_topic_matrix(patent_to_topics_matrix, firm_dir, firm_patents_threshold):
    firms = get_firms(firm_dir)
    firms = [firm for firm in firms if firms[firm] > firm_patents_threshold]
    result = {firm:dict() for firm in firms}
    filenames = get_files_in_directory(firm_dir)
    for filename in filenames:
        with open(filename, "r", encoding="utf-8") as f:
            for line in f:
                splitted = line.strip().split('\t')
                if len(splitted) != 1: # если равно 1, то фирм нет, игнорируем
                    patent_id = int(splitted[0])
                    if patent_id not in patent_to_topics_matrix.keys():
                        #print(f"can't find patent {patent_id}")
                        pass
                    else:
                        for firm in splitted[1:]:
                            if firm in firms:
                                for topic in patent_to_topics_matrix[patent_id]:
                                    if topic in result[firm].keys():
                                        result[firm][topic] += 1
                                    else:
                                        result[firm][topic] = 1
                            else:
                                #print(f"firm {firm} not in firms")
                                pass
    return result

def create_if_not_exist(dirname):
    if not os.path.isdir(dirname):
        os.mkdir(dirname)

def get_root(parent_tree, node):
    while node in parent_tree:
        node = parent_tree[node]
    return node

# взаимодополняемость j-го к i-го предприятию
def calc_complementarity_matrix(firm_to_topic_matrix, topic_tree, tree_customers, tree_children):
    result = np.zeros((len(firm_to_topic_matrix), len(firm_to_topic_matrix),))
    firm_to_index = {firm:i for i, firm in enumerate(firm_to_topic_matrix)}
    index_to_firm = {firm_to_index[firm]:firm for firm in firm_to_index}
    root_topic = get_root(topic_tree, list(topic_tree.keys())[0])
    for i in range(len(firm_to_topic_matrix)):
        for j in range(len(firm_to_topic_matrix)):
            if i == j:
                continue
            a_patents = firm_to_topic_matrix[index_to_firm[i]]
            b_patents = firm_to_topic_matrix[index_to_firm[j]]
            a_topics = set(firm_to_topic_matrix[index_to_firm[i]].keys())
            b_topics = set(firm_to_topic_matrix[index_to_firm[j]].keys())
            done_topics = set()
            for topic in b_patents:
                main_topic = topic
                while True:
                    main_topic = topic_tree[main_topic]
                    if main_topic not in done_topics:
                        done_topics.add(main_topic)
                        subtopics = set(tree_children[main_topic])
                        TN_BC = len(subtopics.intersection(b_topics))
                        TN_ABC = len(subtopics.intersection(a_topics, b_topics))
                        TN_AC = len(subtopics.intersection(a_topics))
                        TN_C = len(subtopics)
                        PN_C = tree_customers[main_topic]
                        PN = tree_customers[root_topic]
                        if TN_C != TN_AC:
                            result[i,j] += (PN_C) * (TN_BC - TN_ABC) / ((TN_C - TN_AC) * PN)
                        else:
                            result[i,j] += (PN_C) * (TN_BC - TN_ABC) / (0.01 * PN)
                    if main_topic == root_topic:
                        break
                        
    return result, index_to_firm

def analyse(patents_threshold):
    open(status_filename, "w").close()
    firm_dir = 'parser_output/firms'
    patent_to_topics_filename = "clusterer_output/patent_to_topic.txt"
    topic_tree_filename = "clusterer_output/topic_tree.txt"
    p_t = get_patent_to_topic_matrix(patent_to_topics_filename)
    topic_tree, tree_customers, tree_children = get_topic_tree(topic_tree_filename)
    f_t = calc_firm_to_topic_matrix(p_t, firm_dir, patents_threshold)
    complementarity_matrix, firms = calc_complementarity_matrix(f_t, topic_tree, tree_customers, tree_children)
    create_if_not_exist("analyser_output")
    with open("analyser_output/firms.txt", "w", encoding="utf-8") as f:
        for firm in firms:
            f.write(f"{firms[firm]}\t{firm}\n")
    np.save("analyser_output/firm_topic.npy", f_t)
    np.save("analyser_output/complementarity.npy", complementarity_matrix)
    with open(status_filename, "w") as f:
        f.write(str(len(f_t)))
    return str(len(f_t))

def read_complementarity_matrix():
    return np.load("analyser_output/complementarity.npy", allow_pickle=True)

def read_firm_to_topic_matrix():
    return np.load("analyser_output/firm_topic.npy", allow_pickle=True)

def read_firm_list():
    firm_dict = {}
    with open("analyser_output/firms.txt", "rt", encoding="utf-8") as f:
        for line in f:
            firmname, index = line.strip().split('\t')
            firm_dict[int(index)] = firmname
    res = [firm_dict[index] for index in sorted(firm_dict.keys())]
    return res
    

def main():
    firm_patents_threshold = 0
    firm_dir = r'input\output\firms'
    patent_to_topics_filename = r"input/patent_to_topic.txt"
    topic_tree_filename = r"input/topic_tree.txt"

    start_time = time()

    p_t = get_patent_to_topic_matrix(patent_to_topics_filename)
    topic_tree, tree_customers, tree_children = get_topic_tree(topic_tree_filename)

    end_pt_time = time()
    print(f"get_patent_to_topic_matrix time: {end_pt_time-start_time}")

    f_t, firms, topics = calc_firm_to_topic_matrix(p_t, firm_dir, firm_patents_threshold)

    end_ft_time = time()
    print(f"get_firm_to_topic_matrix time: {end_ft_time-end_pt_time}")

    create_if_not_exist("output")
    np.save("output/firm_topic.npy", f_t)
    with open("output/firms.txt", "w", encoding="utf-8") as f:
        for firm in firms:
            f.write(f"{firms[firm]}\t{firm}\n")
    with open("output/topics_encoded.txt", "w", encoding="utf-8") as f:
        for topic in topics:
            f.write(f"{topics[topic]}\t{topic}\n")

    end_time = time()
    print(f"total time: {end_time-start_time}")


if __name__=="__main__":
    main()