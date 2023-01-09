import re
import json
import pathlib

import _AEPython as _ae

__ES_class_names = [
    "Array",
    "Application",
    "CameraLayer",
    "CompItem",
    "FileSource",
    "FolderItem",
    "FootageItem",
    "ImportOptions",
    "ItemCollection",
    "KeyframeEase",
    "LayerCollection",
    "LightLayer",
    "MarkerValue",
    "MaskPropertyGroup",
    "OMCollection",
    "OutputModule",
    "PlaceholderSource",
    "Project",
    "Property",
    "PropertyGroup",
    "RenderQueue",
    "RenderQueueItem",
    "RQItemCollection",
    "Settings",
    "Shape",
    "ShapeLayer",
    "SolidSource",
    "System",
    "TextDocument",
    "TextLayer",
    "Viewer",
    "ViewOptions"
]


def _executeScript(code: str):
    code = repr(code)
    return _ae.executeScript(f"__AEPython_executeScript({code})")


def executeScript(code: str):
    ret = _executeScript(code)

    if ret == "null" or ret == "":
        return None

    results = ret.split(",")
    ret_type = results[0]
    if ret_type == "boolean":
        return results[1] == "true"
    elif ret_type == "number":
        v = float(results[1])
        if v == int(v):
            return int(v)
        else:
            return v
    elif ret_type == "string":
        return ret.replace("string,", "", 1)
    elif ret_type == "function":
            return ESFunction(results[2])
    elif ret_type == "object":
        if results[1] in __ES_class_names:
            obj = eval(f"{results[1]}(_id={results[2]})")
            if isinstance(obj, Array):
                return obj.to_list()
            else:
                return obj
        else:
            return ESWrapper(results[2])
    else:
        raise Exception(f"ES type error: {results[0]}")


def __getattr__(name):
    return executeScript(name)


def _toESObject(obj):
    class Encoder(json.JSONEncoder):
        def default(self, obj):
            if isinstance(obj, ESWrapper):
                return repr(obj)
            return json.JSONEncoder.default(self, obj)

    dst =  json.dumps(obj, cls=Encoder)
    return re.sub(r'\"__AEPython_objects\[(\d+)\]\"', r'__AEPython_objects[\1]', dst)


class ESWrapper(object):
    def __init__(self, _id:str):
        super().__setattr__("_es_id", _id)

    def __repr__(self) -> str:
        return f"__AEPython_objects[{self._es_id}]"
    
    def __str__(self) -> str:
        return super().__repr__() + f"(id:{self._es_id})"

    def __del__(self):
        _ae.executeScript(f"__AEPython_deleteObject({self._es_id});")

    def __eq__(self, __o: object) -> bool:
        if isinstance(__o, ESWrapper) == True:
            return executeScript(f"{repr(self)} == {repr(__o)};")
        else:
            return False

    def __getattr__(self, name: str) -> any:
        ret =  executeScript(f"{repr(self)}.{name};")
        if isinstance(ret, ESFunction):
            return ESObjectFunction(self, name)
        else:
            return ret

    def __setattr__(self, __name: str, __value: any) -> None:
        if hasattr(super(), __name):
            super().__setattr__(__name, __value)
        else:
            __value = _toESObject(__value)
            executeScript(f"__AEPython_setattr({self._es_id}, {repr(__name)}, {__value});")


class ESFunction(ESWrapper):
    def __call__(self, *args, **kwds) -> any:
        code = f"__AEPython_callObject({self._es_id}, {_toESObject(args)[1:-1]});"
        return executeScript(code)

class ESObjectFunction():
    def __init__(self, object, function_name):
        self.__object = object
        self.__function_name = function_name

    def __call__(self, *args, **kwds) -> any:
        code = f"{repr(self.__object)}.{self.__function_name}({_toESObject(args)[1:-1]});"
        return executeScript(code)


# ES virtual classes
class Item(ESWrapper):pass
class AVItem(Item):pass
class Layer(ESWrapper):pass
class AVLayer(Layer):pass
class FootageSource(ESWrapper):pass
class PropertyBase(ESWrapper):pass

class Collection(ESWrapper):
    def __iter__(self):
        object.__setattr__(self, "_i", 0)
        return self
    
    def __next__(self):
        length = int(self.__getattr__("length"))
        if self._i >= length:
            raise StopIteration()

        ret = executeScript(f"{repr(self)}[{self._i}];")
        object.__setattr__(self, "_i", self._i + 1)
        return ret
    
    def __getitem__(self, index:int):
        return executeScript(f"{repr(self)}[{index}];")


# ES classes
class Array(ESWrapper):
    def to_list(self):
        dst = []

        length = executeScript(f'{repr(self)}.length')
        for i in range(0, length):
            element = executeScript(f'{repr(self)}[{i}]')
            dst.append(element)

        return dst
 
class Application(ESWrapper):
    def beginUndoGroup(self, name:str):
        _ae.startUndoGroup(name)
    
    def endUndoGroup(self):
        _ae.endUndoGroup()

class CameraLayer(Layer):pass
class CompItem(AVItem):pass
class FileSource(FootageSource):pass
class FolderItem(Item):pass
class FootageItem(AVItem):pass

class ImportOptions(ESWrapper):
    def __init__(self, file: str | pathlib.Path | ESWrapper = None, _id: str = None):
        if _id is None:
            if file is None:
                code = "new ImportOptions()"
            elif isinstance(file, str):
                code = f"new ImportOptions(new File({repr(file)}))"
            elif isinstance(file, pathlib.Path):
                code = f"new ImportOptions(new File({repr(file.as_posix())}))"
            else:
                code = f"new ImportOptions({repr(file)})"
            ret = _executeScript(code)
            _id = ret.split(",")[2]

        super().__init__(_id)

class ItemCollection(Collection):pass

class KeyframeEase(ESWrapper):
    def __init__(self, x=None, y=None, _id: str = None):
        if _id is None:
            ret = _executeScript(f"new KeyframeEase({x}, {y})")
            _id = ret.split(",")[2]

        super().__init__(_id)

class LayerCollection(Collection):pass
class LightLayer(Layer):pass

class MarkerValue(ESWrapper):
    def __init__(self, comment=None, chapter=None, url=None, frameTarget=None,
                 cuePointName=None, params=None, _id: str = None):
        if _id is None:
            comment = repr(comment)
            chapter = "undefined" if chapter is None else repr(chapter)
            url = "undefined" if url is None else repr(url)
            frameTarget = "undefined" if frameTarget is None else repr(frameTarget)
            cuePointName = "undefined" if cuePointName is None else repr(cuePointName)
            params = "undefined" if params is None else repr(params)

            code = f"new MarkerValue({comment}, {chapter}, {url}, {frameTarget}, {cuePointName}, {params})"
            ret = _executeScript(code)
            _id = ret.split(",")[2]

        super().__init__(_id)

class MaskPropertyGroup(ESWrapper):pass
class OMCollection(Collection):pass
class OutputModule(ESWrapper):pass
class PlaceholderSource(ESWrapper):pass
class Project(ESWrapper):pass
class Property(PropertyBase):pass
class PropertyGroup(PropertyBase):pass
class RenderQueue(ESWrapper):pass
class RenderQueueItem(ESWrapper):pass
class RQItemCollection(Collection):pass
class Settings(ESWrapper):pass

class Shape(ESWrapper):
    def __init__(self, _id: str = None):
        if _id is None:
            ret = _executeScript("new Shape()")
            _id = ret.split(",")[2]

        super().__init__(_id)

class ShapeLayer(ESWrapper):pass
class SolidSource(FootageSource):pass
class System(ESWrapper):pass

class TextDocument(ESWrapper):
    def __init__(self, docText="", _id: str = None):
        if _id is None:
            text = repr(docText)
            ret = _executeScript(f"new TextDocument({text})")
            _id = ret.split(",")[2]

        super().__init__(_id)

class TextLayer(AVLayer):pass
class Viewer(ESWrapper):pass
class ViewOptions(ESWrapper):pass
