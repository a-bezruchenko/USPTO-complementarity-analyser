import os

from django.shortcuts import render
from django.http import HttpResponse

from django.http import HttpResponse, JsonResponse
from django.template import loader

import io
import urllib, base64

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from process_clustered_patents import analyse, read_complementarity_matrix, read_firm_to_topic_matrix, read_firm_list

clusterer_status_filename = "cluster_status"
analyser_status_filename = "analyser_status"

def index(request):
    template = loader.get_template('analyser/analyser.html')
    context = {}
    return HttpResponse(template.render(context, request))

def start_analyse(request):
    threshold = int(request.GET["threshold"])
    analyse(threshold)
    return HttpResponse()

# def get_complementarity_heatmap(request):
#     c_m = read_complementarity_matrix()
#     firms = read_firm_list()
#     print(firms)
#     ax = plt.gca()
#     ax.set_xticks(list(range(0, len(c_m), 1)));
#     ax.set_yticks(list(range(0, len(c_m), 1)));
#     #ax.set_xticklabels(firms)
#     #ax.set_yticklabels(firms)
#     ax.set_xticklabels(list(range(0, len(c_m), 1)))
#     ax.set_yticklabels(list(range(0, len(c_m), 1)))
#     ax.tick_params(axis='x', which='both', labelsize=4)
#     ax.tick_params(axis='y', which='both', labelsize=4)
#     plt.imshow(c_m)
#     fig = plt.gcf()
#     #convert graph into dtring buffer and then we convert 64 bit code into image
#     buf = io.BytesIO()
#     fig.savefig(buf,format='png', dpi=1200, bbox_inches='tight')
#     buf.seek(0)
#     string = base64.b64encode(buf.read())
#     uri =  urllib.parse.quote(string)
#     return render(request,'analyser/image.html',{'data':uri})

def get_complementarity_heatmap(request):
    c_m = read_complementarity_matrix()
    return JsonResponse(c_m.tolist(), safe=False)

def get_firm_list(request):
    firms = read_firm_list()
    return JsonResponse(firms, safe=False)

def get_firm_heatmap(request):
    f_t = read_firm_to_topic_matrix()
    
    plt.imshow(f_t)
    fig = plt.gcf()
    #convert graph into dtring buffer and then we convert 64 bit code into image
    buf = io.BytesIO()
    fig.savefig(buf,format='png')
    buf.seek(0)
    string = base64.b64encode(buf.read())
    uri =  urllib.parse.quote(string)
    return render(request,'analyser/image.html',{'data':uri})

amount_of_firms_to_take = 10

def get_complementary_firms(request):
    firm = request.GET["firm"]
    firms = read_firm_list()
    c_m = read_complementarity_matrix()
    try:
        firm_index = firms.index(firm)
        comps = c_m[firm_index]
        comps = {comps[i]: firms[i] for i in range(len(firms))}
        comps = sorted(comps.items(), reverse=True)
        most_complementary = {x[1]:x[0] for x in comps[:amount_of_firms_to_take]}
        return render(request,'analyser/comp_firms.html',{'firms':most_complementary})
    except Exception as e:
        return HttpResponse("<p>Указанная фирма не указана</p>")

def reset(request):

    if os.path.isfile("analyser_status"):
        os.remove("analyser_status")
    return HttpResponse()

def is_done(status_filename):
    try:
        with open(status_filename, "r") as f:
            res = f.read()
        if res == "":
            return False
        else:
            return True
    except Exception:
        return False

def is_working(status_filename):
    try:
        with open(status_filename, "r") as f:
            res = f.read()
        if res == "":
            return True
        else:
            return False
    except Exception:
        return False

def how_many_processed(status_filename):
    try:
        with open(status_filename, "r") as f:
            res = f.read()
        return res
    except Exception:
        return False

def get_status(request):
    if is_working(analyser_status_filename):
        return HttpResponse("working")
    elif is_done(analyser_status_filename):
        return HttpResponse("done "+how_many_processed(analyser_status_filename))
    elif is_done(clusterer_status_filename):
        return HttpResponse("ready to start")
    else:
        return HttpResponse("not ready")

def getFirmHeatmap(request):
    firm = request.GET["firm"]
    data = list(range(int(firm)))
    return get_heatmap_to_responce(request, data)

def get_heatmap_to_responce(request, data):
    plt.plot(data)
    fig = plt.gcf()
    #convert graph into dtring buffer and then we convert 64 bit code into image
    buf = io.BytesIO()
    fig.savefig(buf,format='png')
    buf.seek(0)
    string = base64.b64encode(buf.read())
    uri =  urllib.parse.quote(string)
    return render(request,'analyser/image.html',{'data':uri})

def get_firm_choosing_list(request):
    firms = read_firm_list()
    return render(request,'analyser/choosing_list.html',{'firms':firms})