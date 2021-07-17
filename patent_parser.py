import re
import os
import sys
from pprint import pprint
from bs4 import BeautifulSoup as BS
import time
from multiprocessing import Process

parallel_processes_count = 10
max_patents = None
parser_output_dir = "parser_output"
status_filename = "parser_status"

#permitted_classification_types = ["classification-ipcr"]
#classification_filter = {"classification-ipcr":["F", "G", "H"]}

def split_xml(text: str):
    splitter = '<?xml version="1.0" encoding="UTF-8"?>'
    splitted = text.split(splitter)
    splitted = list(filter(lambda x: x != '', splitted))
    return splitted


def get_text_field(tag, field_name: str):
    field = tag.find(field_name)
    try:
        if field:
            text_field = field.text.strip().replace('\t', ' ')
            return text_field
        else:
            return None
    except AttributeError:
        print("Ошибка при обращении к полю" + field_name)
        return None

def parse_patent(patent_text):
    soup = BS(patent_text, features="lxml")
    # Identification of a patent application.
    temp = soup.find("application-reference")
    if temp:
        application_reference = {'doc_number': get_text_field(temp, "doc-number"),
                                 'country': get_text_field(temp, "country"),
                                 'date': get_text_field(temp, "date")}
    else:
        application_reference = None
    # Identification of a published patent document.
    temp = soup.find("publication-reference")
    if temp:
        publication_reference = {'doc_number': get_text_field(temp, "doc-number"),
                                 'country': get_text_field(temp, "country"),
                                 'date': get_text_field(temp, "date")}
    else:
        publication_reference = None
    assignees = []
    for assignee in soup.findAll("assignee"):
        if get_text_field(assignee, "orgname"):
            assignees.append(get_text_field(assignee, "orgname"))
    classification_type = None
    main_classification = None
    for type in ("classification-ipc", "classification-ipcr", "classification-locarno"):
        tag = soup.find(type)
        if tag:
            classification_type = type
            if type == "classification-ipcr":
                section_tag = tag.find("section")
                class_tag = tag.find("class")
                subclass_tag = tag.find("subclass")
                if section_tag and class_tag and subclass_tag:
                    patent_section = section_tag.text.strip()
                    patent_class = class_tag.text.strip()
                    patent_subclass = subclass_tag.text.strip()
                    main_classification = f"{patent_section}\t{patent_class}\t{patent_subclass}"
                    break
                else:
                    continue
            else:
                main_classification_tag = tag.find("main-classification")
                if main_classification_tag:
                    main_classification = main_classification_tag.text.strip()
                    break
                else:
                    continue
    description_tag = soup.find("description")
    if description_tag:
        description = description_tag.text
    else:
        return None
    claims = [x.text for x in soup.findAll("claim-text")]
    claims = '\n'.join(claims)
    inventors = []
    applicants = soup.find("applicants")
    if applicants:
        for content in applicants.contents:
            if content != '\n':
                inventor = {'first-name': get_text_field(content, "first-name"),
                            'last-name': get_text_field(content, "last-name")}
                inventors.append(inventor)
    abstract = str(None)
    tag = soup.find("abstract")
    if tag:
        problem_tag = tag.find("abst-problem")
        solution_tag = tag.find("abst-solution")
        if problem_tag and solution_tag:
            abstract = problem_tag.text + " " + solution_tag.text
        else:
            abstract = tag.text
    # tag = soup.find("classification-national")
    # if tag:
    #     country = tag.find("country").text.strip()
    #     national_classification = tag.find("main-classification").text.strip()
    # else:
    #     country = None
    #     national_classification = None
    return {
                "id": int(application_reference["doc_number"]),
                "application_reference": application_reference,
                "publication_reference": publication_reference,
                "abstract": abstract,
                "main_classification_type": str(classification_type),
                "main_classification": str(main_classification),
                "description" : description,
                "claims": claims,
                "applicants": inventors,
                "assignees":assignees
            }

def create_if_not_exist(dirname):
    if not os.path.isdir(dirname):
        os.mkdir(dirname)

def get_name(filename):
    return filename[filename.rfind('/')+1:filename.rfind('.')]

def process_file(filename):
    print("Started processing " + filename)
    start_time = time.time()
    file_res = []
    with open(filename, "r") as f:
        text = f.read()

    res = split_xml(text)

    for text_num, text in enumerate(res):
        if text_num % 100 == 0:
            print(f"{filename} : {text_num}")
        if max_patents and text_num > max_patents:
            break
        parsed_patent = parse_patent(text)
        if parsed_patent:
            file_res.append(parsed_patent)
            #validType = parsed_patent["main_classification_type"] in permitted_classification_types
            #if validType:
            #    class_parts = parsed_patent["main_classification"].split()
            #    validSection = class_parts[0] in classification_filter[parsed_patent["main_classification_type"]]
            #    if validSection:
            #        file_res.append(parsed_patent)
            #     else:
            #         print(f"wrong section: {class_parts[0]}")
            # else:
            #     print(f'wrong type: {parsed_patent["main_classification_type"]}')

    create_if_not_exist(parser_output_dir)
    create_if_not_exist(parser_output_dir+"/data")
    create_if_not_exist(parser_output_dir+"/firms")
    create_if_not_exist(parser_output_dir+f"/info")
    create_if_not_exist(parser_output_dir+f"/data/{get_name(filename)}")
    for patent in file_res:
        with open(parser_output_dir+f"/data/{get_name(filename)}/{patent['id']}", "w", encoding="utf-8") as f:
            f.write(patent["claims"] + '\n')
            f.write(patent["description"] + '\n')
            f.write(patent["abstract"] + '\n')
    with open(parser_output_dir+f"/info/info_{get_name(filename)}", "w", encoding="utf-8") as f:
        for patent in file_res:
            f.write(f"{patent['id']}\t{patent['main_classification_type']}\t{patent['main_classification']}\n")
    # firms = set()
    # for patent in file_res:
    #     for a in patent["assignees"]:
    #         if a not in firms:
    #             firms.add(a)
    # firms = {firm:id for id, firm in enumerate(firms)}
    # with open(f"output/firms/{get_name(filename)}/firms", "w", encoding="utf-8") as f:
    #     for firm in firms:
    #         f.write(f"{firm}\t{firms[firm]}\n")
    with open(parser_output_dir+f"/firms/firms_{get_name(filename)}", "w", encoding="utf-8") as f:
        for patent in file_res:
            patent_firms = patent["assignees"]
            output_firms = '\t'.join(patent_firms)
            f.write(f"{patent['id']}\t{output_firms}\n")

    end_time = time.time()
    print(f"Finished processing {filename}, time: {end_time-start_time}")

def process_files(filenames):
    for name in filenames:
        process_file(name)

def process_files_multiprocess(filenames):
    filenames_list = []
    for i in range(parallel_processes_count):
        start = i * len(filenames) / parallel_processes_count
        end = (i+1) * len(filenames) / parallel_processes_count
        if i == parallel_processes_count:
            end = len(filenames)
        start = int(start)
        end = int(end)
        filenames_list.append(filenames[start:end])
    filenames_list = filenames_list
    processes = []
    for sublist in filenames_list:
        p = Process(target = process_files, args = [sublist])
        p.start()
        processes.append(p)
    for p in processes:
        p.join()

def parse_dir(dirname):
    open(status_filename, "w").close()
    names = [dirname]
    filenames = []
    i = 0
    while i < len(names):
        if os.path.isdir(names[i]):
            names += list(map(lambda x: f"{names[i]}/{x}", os.listdir(names[i])))
        i += 1
    filenames = [name for name in names if os.path.isfile(name)]
    process_files_multiprocess(filenames)
    with open(status_filename, "w") as f:
        f.write(str(len(filenames)))
    return len(filenames)

def main():
    names = sys.argv[1:]
    filenames = []
    i = 0
    while i < len(names):
        if os.path.isdir(names[i]):
            names += list(map(lambda x: f"{names[i]}/{x}", os.listdir(names[i])))
        i += 1
    filenames = [name for name in names if os.path.isfile(name)]
    #print("Filenames:\n")
    #pprint(filenames)
    process_files_multiprocess(filenames)


    

if __name__=="__main__":
    main()