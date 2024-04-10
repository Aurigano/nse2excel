from django.shortcuts import render, redirect
import requests
import sys
from subprocess import run, PIPE, Popen, CREATE_NEW_CONSOLE, DETACHED_PROCESS
from django.conf import settings
import os
import json

global subprocess_obj


def sampleFn(argReq):
    data = requests.get("https://reqres.in/api/users")
    # print(data.text)
    data = data.text
    return render(argReq, "home.html", {"data": data})


def defaultFn(argReq):
    data = requests.get("https://reqres.in/api/users")
    return render(argReq, "home.html", {"data0": "in-home"})


def external(request):
    global subprocess_obj

    filename = request.POST.get("filename")
    interval = request.POST.get("interval")
    option = request.POST.get("option")
    expiry = request.POST.get("expiry")
    print(filename, interval, option, expiry)
    inp_dict = {
        "filename": filename,
        "interval": interval,
        "option": option,
        "expiry": expiry,
    }
    # inp_dict = [
    #     filename,
    #     interval,
    #     option,
    #     expiry,
    # ]
    inp_dict_str = json.dumps(inp_dict)

    script_path = os.path.join(settings.BASE_DIR, "src//", "nsepoll.py")
    print(script_path)

    ## for running in the same thread
    # out = run(
    #     [sys.executable, "D:\python\longPollPoc//test.py", inp],
    #     shell=False,
    # )

    ## Popen starts a new console with the given flags, not hindering with whats going on
    subprocess_obj = Popen(
        [sys.executable, script_path, inp_dict_str],
        shell=False,
        creationflags=CREATE_NEW_CONSOLE,
    )

    # Wait for the process to complete
    # stdout, stderr = subprocess_obj.communicate()

    # # Print stdout and stderr
    # print("Output:", stdout.decode(sys.stdout.encoding))
    # print("Errors:", stderr.decode(sys.stderr.encoding))

    # # Check the return code
    # if subprocess_obj.returncode != 0:
    #     print("Error occurred, return code:", subprocess_obj.returncode)

    print("started", subprocess_obj)
    return render(request, "home.html", {"data1": "started"})


def stopFn(request):
    global subprocess_obj

    # terminate subprocess
    subprocess_obj.terminate()
    # subprocess_obj.kill()
    # return render(request, "home.html", {"data2": "stopped"})
    return render(request, "home.html", {"data2": "stopped"})


def contract(self, req, param1):
    # Access param1 and param2 as needed
    return render(req, "home.html", {"contract": param1})
