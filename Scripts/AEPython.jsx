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

__AEPython_objects = {}
__AEPython_objects_count = 0;

function __AEPython_executeScript(code) {
    try {
        const ret = eval(code)
    } catch (e) {
        var error_message = 'print("' + e.message + '", file=sys.stderr)';
        Python.exec(error_message);
        throw new Error(e.message);
    }

    if (ret === null || ret === undefined) { return null; }

    const type = typeof (ret);
    if (type == "object" || type == "function") {
        __AEPython_objects_count = Math.round(__AEPython_objects_count + 1);
        __AEPython_objects[__AEPython_objects_count] = ret;
        if (type == "object"){
            return [type, ret.constructor.name, __AEPython_objects_count];
        }else{
            return [type, null, __AEPython_objects_count];
        }
    } else {
        return [type, ret];
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

function __AEPython_callObject(id, _args) {
    const func = __AEPython_objects[id];
    
    var code = "func(";
    for(var i=1; i < arguments.length; i++){
        code += "arguments[" + i + "]";
        if (i < arguments.length - 1){code += ", ";}
    }
    code += ");";

    return eval(code);
}
