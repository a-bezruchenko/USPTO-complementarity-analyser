import sys
import os
from pathlib import Path

from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem.porter import PorterStemmer
from sampler import HierarchicalLDA
import numpy as np
import string
import pickle

import nltk

from time import time

clusterer_status_filename = "cluster_status"

#nltk.download('stopwords')
#nltk.download('punkt')

display_topics = 50   # the number of iterations between printing a brief summary of the topics so far
n_words = 5           # the number of most probable words to print for each topic after model estimation
with_weights = False  # whether to print the words with the weights

def filename_filter(input_dir, filter_set, is_whitelist = False):
    for address, _, filenames in os.walk(input_dir):
        for filename in filenames:
            if (is_whitelist and filename in filter_set) or (not is_whitelist and filename not in filter_set):
                full_filename = Path(address) / Path(filename)
                yield full_filename

def get_filtered_patent_names(info_dir, filter):
    target_classification = filter.split(' ')
    res = set()
    for address, _, filenames in os.walk(info_dir):
        for filename in filenames:
            full_filename = Path(address) / Path(filename)
            with open(full_filename, "r", encoding="utf-8") as f:
                for line in f:
                    patent_name, *classification = line.strip().split('\t')
                    is_good = True
                    if len(target_classification) <= len(classification):
                        for i in range(len(target_classification)):
                            if classification[i] != target_classification[i]:
                                is_good = False
                                break
                        if is_good:
                            res.add(patent_name)
    return res

def cluster_files(n_samples, alpha, gamma, eta, num_levels, filter_str = ""):
    open(clusterer_status_filename, "w").close()
    input_dir = "parser_output/data"
    info_dir = "parser_output/info"
    output_dir = "clusterer_output"
    if filter_str == "":
        corpus, vocab, patents_map = preprocess(filename_filter(input_dir, set()))
    else:
        patents_to_cluster = get_filtered_patent_names(info_dir, filter_str)
        corpus, vocab, patents_map = preprocess(filename_filter(input_dir, patents_to_cluster, is_whitelist=True))
    tree = cluster_patents(corpus, vocab, n_samples, alpha, gamma, eta, num_levels, display_topics, n_words, with_weights)
    save_patents_clustering(tree, patents_map, output_dir)
    with open(clusterer_status_filename, "w") as f:
        f.write(str(len(patents_map)))
    return len(patents_map)


def main():
    n_samples = 10       # no of iterations for the sampler
    alpha = 10.0          # smoothing over level distributions
    gamma = 1.0           # CRP smoothing parameter; number of imaginary customers at next, as yet unused table
    eta = 0.1             # smoothing over topic-word distributions
    num_levels = 3        # the number of levels in the tree
    times = [time()]
    input_dir = sys.argv[1]
    if len(sys.argv) == 3:
        output_dir = sys.argv[2]
    else:
        output_dir = None
    corpus, vocab, patents_map = preprocess(filename_filter(input_dir, set()))
    times.append(time())
    print(f"Preprocessing finished in {times[1]-times[0]}\n")
    tree = cluster_patents(corpus, vocab, n_samples, alpha, gamma, eta, num_levels, display_topics, n_words, with_weights)
    times.append(time())
    print(f"Clustering finished in {times[2]-times[1]}\n")
    if output_dir:
        save_patents_clustering(tree, patents_map, output_dir)
    times.append(time())
    print(f"Preprocessing finished in {times[1]-times[0]}\n")
    print(f"Clustering finished in {times[2]-times[1]}\n")
    print(f"Saving finished in {times[3]-times[2]}\n")


# def get_patent_id(filename):
#     return int(filename[filename.rfind('/')+1:])

# def get_files_in_directory(dir_name):
#     names = [dir_name]
#     i = 0
#     while i < len(names):
#         if os.path.isdir(names[i]):
#             names += list(map(lambda x: f"{names[i]}/{x}", os.listdir(names[i])))
#         i += 1
#     return [name for name in names if os.path.isfile(name)]

def create_if_not_exist(dirname):
    if not os.path.isdir(dirname):
        os.mkdir(dirname)

def preprocess(filenames_iterator):
    stopset = stopwords.words('english') + list(string.punctuation) + ['will', 'also', 'said','claim','fig','and/or']
    corpus = []
    all_docs = []
    vocab = set()
    patents_map = {} # corpus index to patent id map
    stemmer = PorterStemmer()
    filenum = 0
    for full_filename in filenames_iterator:
            filenum += 1
            with open(full_filename, "r", encoding="utf-8") as f:
                try:
                    doc = f.read().splitlines() 
                    doc = filter(None, doc) # remove empty string
                    doc = '. '.join(doc)
                    intab = string.punctuation + '0123456789'
                    outtab = " "*len(intab)
                    trantab = str.maketrans(intab, outtab)
                    doc = doc.translate(trantab)
                    all_docs.append(doc)
                    tokens = word_tokenize(str(doc))
                    filtered = []
                    for w in tokens:
                        w = stemmer.stem(w.lower()) # use Porter's stemmer
                        if len(w) < 3:              # remove short tokens
                            continue
                        if w in stopset:            # remove stop words
                            continue
                        filtered.append(w)
                    vocab.update(filtered)
                    corpus.append(filtered)
                    patents_map[len(corpus)-1] = int(full_filename.stem)
                except UnicodeDecodeError:
                    print('Failed to load', full_filename)
            if filenum != 0 and filenum % 100 == 0:
                print(f"processed {filenum} files")
                #break
    vocab = sorted(list(vocab))
    vocab_index = {}
    for i, w in enumerate(vocab):
        vocab_index[w] = i
    new_corpus = []
    for doc in corpus:
        new_doc = []
        for word in doc:
            word_idx = vocab_index[word]
            new_doc.append(word_idx)
        new_corpus.append(new_doc)
    return new_corpus, vocab, patents_map

def cluster_patents(corpus, vocab, n_samples, alpha, gamma, eta, num_levels, display_topics, words, with_weights):
    seed = 42
    hlda = HierarchicalLDA(corpus, vocab, alpha=alpha, gamma=gamma, eta=eta, num_levels=num_levels, seed=seed)
    print("hlda initialized")
    hlda.estimate(n_samples, display_topics=display_topics, n_words=n_words, with_weights=with_weights)
    return hlda

def get_children_and_self(node):
    nodes = [node]
    for child in node.children:
        nodes += get_children_and_self(child)
    return nodes


def save_zipped_pickle(obj, filename, protocol=-1):
    with open(filename, 'wb') as f:
        pickle.dump(obj, f, protocol)
        

def load_zipped_pickle(filename):
    with open(filename, 'rb') as f:
        loaded_object = pickle.load(f)
        return loaded_object


def save_patents_clustering(tree, patents_map, output_dir):
    create_if_not_exist(output_dir)
    with open(output_dir+"/patent_to_topic.txt", "w", encoding="utf-8") as f:
        for leaf_num in range(len(tree.document_leaves)):
            f.write(f"{patents_map[leaf_num]}\t{tree.document_leaves[leaf_num].node_id}\n")
    nodes = get_children_and_self(tree.root_node)
    with open(output_dir+"/topic_tree.txt", "w", encoding="utf-8") as f:
        for node in nodes:
            if node.parent != None:
                f.write(f"{node.node_id}\t{node.customers}\t{node.parent.node_id}\n")
            else:
                f.write(f"{node.node_id}\t{node.customers}\n")
    with open(output_dir+"/keywords.txt", "w", encoding="utf-8") as f:
        for node in nodes:
            f.write(f"{node.node_id}\t{node.get_top_words(n_words, with_weights)}\n")


if __name__=="__main__":
    main()
