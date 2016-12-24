/* -*-mode:c++; tab-width: 4; indent-tabs-mode: nil; c-basic-offset: 2 -*- */

#include <Python.h>
#include <iostream>
#include <string>
#include <vector>

#include "launch.hh"

using namespace std;

static PyObject *pylaunch_launchpar(PyObject *self, PyObject *args);

// method table and initialization
static PyMethodDef pylaunch_Methods[] = {
    {"launchpar", pylaunch_launchpar, METH_VARARGS, "Launch many lambdas in parallel."},
    {NULL, NULL, 0, NULL }
};
PyMODINIT_FUNC initpylaunch(void) {
    cerr << "Initializing pylaunch... ";
    (void) Py_InitModule("pylaunch", pylaunch_Methods);
    cerr << "done." << endl;
}

// call launchpar from python
static PyObject *pylaunch_launchpar(PyObject *self __attribute__((unused)), PyObject *args) {
    int nlaunch;
    char *fn_name, *akid, *secret;
    PyObject *payloads_obj;
    PyObject *lambda_regions_obj;
    if (! PyArg_ParseTuple(args, "issssO!", &nlaunch, &fn_name, &akid, &secret, &PyList_Type, &payloads_obj, &PyList_Type, &lambda_regions_obj)) {
        return NULL;
    }

    vector<string> payloads;
    size_t npayloads = PyList_Size(payloads_obj);
    for (size_t i = 0; i < npayloads; i++) {
      PyObject *payload = PyList_GetItem(payloads_obj, i);
      payloads.emplace_back(string(PyString_AsString(payload)));
    }

    vector<string> lambda_regions;
    size_t nregions = PyList_Size(lambda_regions_obj);
    for (size_t i = 0; i < nregions; i++) {
        PyObject *region = PyList_GetItem(lambda_regions_obj, i);
        lambda_regions.emplace_back(string(PyString_AsString(region)));
    }

    launchpar(nlaunch, string(fn_name), string(akid), string(secret), payloads, lambda_regions);

    Py_RETURN_NONE;
}
