import os
import numpy as np
from time import time

topic_threshold = 0.15
firm_patents_threshold = 30

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
def get_patent_to_topic_matrix(filename):
    with open(filename, "r") as f:
        patent_to_topics = f.readlines()
    splitted = [split_line(line) for line in patent_to_topics]
    filtered = {id:filter_threshold(data, topic_threshold) for id, data in splitted}
    return filtered

def show_ones(x):
    if x == 0:
        return ' '
    else:
        return '*'

def print_data(filtered):
    for id, data in filtered:
        print(f"{id:08d}|{''.join(list(map(show_ones,data)))}")

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
    

def get_firm_to_topic_matrix(patent_to_topics_matrix, firm_dir, topics_count):
    firms = get_firms(firm_dir)
    firms = [firm for firm in firms if firms[firm] > firm_patents_threshold]
    firms = {firm:i for i, firm in enumerate(firms)}
    result = np.zeros((len(firms), topics_count,))
    filenames = get_files_in_directory(firm_dir)
    for filename in filenames:
        with open(filename, "r", encoding="utf-8") as f:
            for line in f:
                splitted = line.strip().split('\t')
                if len(splitted) != 1: # если равно 1, то фирм нет, игнорируем
                    patent_id = int(splitted[0])
                    if patent_id not in patent_to_topics_matrix.keys():
                        pass
                        #print(f"can't find patent {patent_id}")
                    else:
                        for firm in splitted[1:]:
                            if firm in firms.keys():
                                for topic in patent_to_topics_matrix[patent_id]:
                                    result[firms[firm], topic] += 1
    return result, firms

def create_if_not_exist(dirname):
    if not os.path.isdir(dirname):
        os.mkdir(dirname)

def main():
    create_if_not_exist("output")
    start_time = time()
    p_t = get_patent_to_topic_matrix("input/doc_topics.txt")
    end_pt_time = time()
    print(f"get_patent_to_topic_matrix time: {end_pt_time-start_time}")
    f_t, firms = get_firm_to_topic_matrix(p_t, r"C:\Users\User\Desktop\универ\диплом\output\firms", 100)
    end_ft_time = time()
    print(f"get_firm_to_topic_matrix time: {end_ft_time-end_pt_time}")
    np.save("output/firm_topic.npy", f_t)
    with open("output/firms.txt", "w", encoding="utf-8") as f:
        for firm in firms:
            f.write(f"{firms[firm]}\t{firm}\n")
    end_time = time()
    print(f"total time: {end_time-start_time}")


if __name__=="__main__":
    main()