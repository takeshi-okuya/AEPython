Python = new ExternalObject("lib:" + BridgeTalk.getAppPath(BridgeTalk.appName) + "/../Plug-ins/AEPython/AEPython.aex")

Python.execFile = function (path) {
    const file = new File(path);
    if (file.exist == false) {
        alert(file.fsName + " not found.");
        return;
    }

    if (file.open("r") == false) {
        alert("Failed to open " + file.fsName);
        return;
    }
    const code = file.read();
    file.close();

    Python.exec("__file__ = r'" + file.fsName + "'");
    Python.exec(code);
    Python.exec("del __file__");
}

Python.import = function (name) {
    return Python.eval("__import__('importlib').import_module('" + name + "')");
}

Python.reload = function (module) {
    return Python.import("importlib").callattr("reload", [module]);
}

Python.print = function () {
    var code = "print(";
    for (var i = 0; i < arguments.length; i++) {
        code += __AEPython_toPyExpression(arguments[i]) + ", ";
    }
    code += ")";
    Python.eval(code);
}

__AEPython_objects = {}
__AEPython_objects_count = 0;

function __AEPython_addObject(obj) {
    __AEPython_objects_count = Math.round(__AEPython_objects_count + 1);
    __AEPython_objects[__AEPython_objects_count] = obj;
    return __AEPython_objects_count;
}

function __AEPython_toPyExpression(v) {
    var type = typeof v;
    if (type == "number") { return v.toString(); }
    else if (type == "string") { return '"' + v.replace(/\\/g, "\\\\").replace(/"/g, '\\"').replace(/\r\n|\n\r|\r|\n/g, '\\n') + '"'; }
    else if (v === null || v === undefined) { return "None"; }
    else if (type == "boolean") { return v ? "True" : "False"; }
    else if (v instanceof __AEPython_PyObject) { return "_py_objects[" + v.id + "]"; }
    else if (type == "function") { return "ESFunction(_ESId(" + __AEPython_addObject(v) + "))"; }
    else { return "_create_ESWrapper('" + v.constructor.name + "'," + __AEPython_addObject(v) + ")"; }
}

function __AEPython_executeScript(code) {
    try {
        const ret = eval(code)
        return __AEPython_toPyExpression(ret)
    } catch (e) {
        var error_message = 'print("' + e.message + '", file=sys.stderr)';
        Python.exec(error_message);
        throw new Error(e.message);
    }
}

function __AEPython_setattr(id, _name, value) {
    const obj = __AEPython_objects[id];
    const code = "obj." + _name + " = value";
    eval(code)
}

function __AEPython_deleteObject(id) {
    delete __AEPython_objects[id];
}

__AEPython_PyObject = function (id) {
    this.id = id;
    this.base = new AEPython_PyObjectBase(id);
}

__AEPython_PyObject.prototype.callattr = function (name, args, keyArgs) {
    args = (args === undefined) ? [] : args;
    keyArgs = (keyArgs === undefined) ? {} : keyArgs;

    var code = "_py_objects[" + this.id + "]." + name + "(*[";

    for (var i = 0; i < args.length; i++) {
        code += __AEPython_toPyExpression(args[i]) + ", ";
    }

    code += "], **{";

    for (var key in keyArgs) {
        code += '"' + key + '":' + __AEPython_toPyExpression(keyArgs[key]) + ", ";
    }

    code += "})";

    return Python.eval(code);
}

__AEPython_PyObject.prototype.getattr = function (name) {
    var code = "getattr(_py_objects[" + this.id + "], '" + name + "')";
    return Python.eval(code);
}

__AEPython_PyObject.prototype.setattr = function (name, value) {
    var code = "setattr(_py_objects[" + this.id + "], '" + name + ", " + __AEPython_toPyExpression(value) + ")";
    Python.eval(code);
}

__AEPython_PyObject.prototype.getitem = function (key) {
    var code = "_py_objects[" + this.id + "].__getitem__(" + key + ")";
    return Python.eval(code);
}

__AEPython_PyObject.prototype.setitem = function (key, value) {
    var _key = __AEPython_toPyExpression(key);
    var _value = __AEPython_toPyExpression(value)
    var code = "_py_objects[" + this.id + "].__setitem__(" + _key + ", " + _value + ")";
    return Python.eval(code);
}

__AEPython_PyObject.prototype.toString = function () {
    return "[PyObject " + this.callattr("__str__") + "]";
}
