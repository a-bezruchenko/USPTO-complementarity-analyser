from django.shortcuts import render
from django.http import HttpResponse

from django.http import HttpResponse
from django.template import loader

from cluster import cluster_files
import os

parser_status_filename = "parser_status"
clusterer_status_filename = "cluster_status"

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

def is_ready_to_cluster():
    return is_done(parser_status_filename) and not is_working(clusterer_status_filename)

def get_clustering_status(request):
    if is_working(clusterer_status_filename):
        return HttpResponse("working")
    elif is_working(parser_status_filename):
        return HttpResponse("not ready")
    elif is_done(clusterer_status_filename):
        return HttpResponse("done "+how_many_processed(clusterer_status_filename))
    elif is_done(parser_status_filename):
        return HttpResponse("ready to start")
    else:
        return HttpResponse("not ready")

def start_clustering(request):
    alpha = float(request.GET['alpha'])
    gamma = float(request.GET['gamma'])
    eta = float(request.GET['eta'])
    n = int(request.GET['n'])
    L = int(request.GET['L'])
    filter_str = request.GET['filter_str']
    if is_ready_to_cluster():
        res = cluster_files(n_samples=n, alpha=alpha, gamma=gamma, eta=eta, num_levels=L, filter_str=filter_str)
    return HttpResponse(str(res))

def index(request):
    template = loader.get_template('clusterer/clusterer.html')
    context = {}
    return HttpResponse(template.render(context, request))

def reset(request):

    if os.path.isfile("cluster_status"):
        os.remove("cluster_status")
    return HttpResponse()