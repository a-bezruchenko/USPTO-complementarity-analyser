from django.shortcuts import render
from django.http import HttpResponse

from django.http import HttpResponse
from django.template import loader

from patent_parser import parse_dir
import os
from os.path import isfile

status_filename = "parser_status"

def index(request):
    template = loader.get_template('parser_module/parser.html')
    context = {}
    return HttpResponse(template.render(context, request))

def wait_for_parse_to_complete(request):
    pass

def get_parsing_status(request):
    if is_parsing():
        return HttpResponse("working")
    elif is_parsed():
        return HttpResponse("done "+how_many_parsed())
    else:
        return HttpResponse("ready to start")

def is_parsing():
    try:
        with open(status_filename, "r") as f:
            res = f.read()
        if res == "":
            return True
        else:
            return False
    except Exception:
        return False


def is_parsed():
    try:
        with open(status_filename, "r") as f:
            res = f.read()
        if res == "":
            return False
        else:
            return True
    except Exception:
        return False

def how_many_parsed():
    try:
        with open(status_filename, "r") as f:
            res = f.read()
        return res
    except Exception:
        return False

def start_parsing(request):
    input_dir = request.GET['input_dir']
    if not is_parsing():
        res = parse_dir(input_dir)
    return HttpResponse(str(res))

def reset(request):

    if os.path.isfile("parser_status"):
        os.remove("parser_status")
    return HttpResponse()