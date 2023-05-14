import pathlib

import _AEPython as _ae

__ES_class_names = [
    "Array",
    "File",
    "Folder",
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


class _ESId(str):pass


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
        return ESFunction(_ESId(results[2]))
    elif ret_type == "object":
        if results[1] in __ES_class_names:
            cls = eval(results[1])
            return cls(_id=_ESId(results[2]))
        else:
            return ESWrapper(_ESId(results[2]))
    else:
        raise Exception(f"ESTypeError: {results[0]}")


def __getattr__(name):
    return executeScript(name)


def _to_ES_expression(obj):
    if obj is None:
        return "null"
    elif isinstance(obj, bool):
        return "true" if obj is True else "false"
    elif isinstance(obj, (int, float, str)):
        return repr(obj)
    elif isinstance(obj, ESWrapper):
        return f"__AEPython_objects[{obj._es_id}]"
    else:
        raise TypeError


class ESWrapper(object):
    def __init__(self, _id: _ESId):
        if isinstance(_id, _ESId) == False:
            raise Exception(f"IdTypeError:{type(_id)}:{_id}")

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
        ret = executeScript(f"{repr(self)}.{name};")
        if isinstance(ret, ESFunction):
            return ESObjectFunction(self, name)
        else:
            return ret

    def __setattr__(self, __name: str, __value: any) -> None:
        if hasattr(super(), __name):
            super().__setattr__(__name, __value)
        else:
            __value = _to_ES_expression(__value)
            executeScript(f"__AEPython_setattr({self._es_id}, {repr(__name)}, {__value});")

class ESFunction(ESWrapper):
    def __call__(self, *args, **kwds) -> any:
        args = f"{', '.join(_to_ES_expression(arg) for arg in args)}"
        code = f"""var __func={repr(self)};
                   __func({args});"""
        return executeScript(code)

class ESObjectFunction():
    def __init__(self, object: ESWrapper, function_name: str):
        self.__object = object
        self.__function_name = function_name

    def __call__(self, *args, **kwds) -> any:
        args = f"{', '.join(_to_ES_expression(arg) for arg in args)}"
        code = f"{repr(self.__object)}.{self.__function_name}({args});"
        return executeScript(code)


# ES classes
class Array(ESWrapper):
    def __init__(self, _id: _ESId = None, *args):
        if isinstance(_id, _ESId):
            if len(args) > 0:
                raise TypeError
        else:
            if _id is None and len(args) == 0:
                id = _executeScript("[]").split(",")[2]
            elif isinstance(_id, int) and _id >= 0 and len(args) == 0:
                id = _executeScript(f"Array({_id})").split(",")[2]
            else:
                values = [_id] + list(args)
                code = f"[{','.join([_to_ES_expression(v) for v in values])}];"
                id = _executeScript(code).split(",")[2]
            _id = _ESId(id)

        super().__init__(_id)
        self.__iter__()

    def __iter__(self):
        object.__setattr__(self, "_i", 0)
        return self

    def __next__(self):
        length = int(self.length)
        if self._i == length:
            raise StopIteration()

        ret = executeScript(f"{repr(self)}[{self._i}];")
        object.__setattr__(self, "_i", self._i + 1)
        return ret

    def __getitem__(self, index: int):
        return executeScript(f"{repr(self)}[{index}];")
    
    def __len__(self):
        return int(self.length)

    def __str__(self):
        return super().__str__() + "[" + executeScript(f"{repr(self)}.toString()") + "]"

class File(ESWrapper):
    def __init__(self, path: str | pathlib.Path = "", _id: _ESId = None):
        if _id is None:
            ret = _executeScript(f"new File({repr(str(path))});")
            _id = _ESId(ret.split(",")[2])

        super().__init__(_id)

class Folder(ESWrapper):
    def __init__(self, path: str | pathlib.Path = "", _id: _ESId = None):
        if _id is None:
            ret = _executeScript(f"new Folder({repr(str(path))});")
            _id = _ESId(ret.split(",")[2])

        super().__init__(_id)


# ES virtual classes
class Item(ESWrapper):pass
class AVItem(Item):pass
class Layer(ESWrapper):pass
class AVLayer(Layer):pass
class FootageSource(ESWrapper):pass
class PropertyBase(ESWrapper):pass

class Collection(ESWrapper):
    def __iter__(self):
        object.__setattr__(self, "_i", 1)
        return self

    def __next__(self):
        length = int(self.length)
        if self._i == length + 1:
            raise StopIteration()

        ret = executeScript(f"{repr(self)}[{self._i}];")
        object.__setattr__(self, "_i", self._i + 1)
        return ret

    def __getitem__(self, index: int):
        return executeScript(f"{repr(self)}[{index}];")


# ES AE classes
class Application(ESWrapper):
    def beginUndoGroup(self, name: str):
        _ae.startUndoGroup(name)

    def endUndoGroup(self):
        _ae.endUndoGroup()

class CameraLayer(Layer):pass
class CompItem(AVItem):pass
class FileSource(FootageSource):pass
class FolderItem(Item):pass
class FootageItem(AVItem):pass

class ImportOptions(ESWrapper):
    def __init__(self, file: str | pathlib.Path | ESWrapper = None, _id: _ESId = None):
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
            _id = _ESId(ret.split(",")[2])

        super().__init__(_id)

class ItemCollection(Collection):pass

class KeyframeEase(ESWrapper):
    def __init__(self, x=None, y=None, _id: _ESId = None):
        if _id is None:
            ret = _executeScript(f"new KeyframeEase({x}, {y})")
            _id = _ESId(ret.split(",")[2])

        super().__init__(_id)

class LayerCollection(Collection):pass
class LightLayer(Layer):pass

class MarkerValue(ESWrapper):
    def __init__(self, comment=None, chapter=None, url=None, frameTarget=None,
                 cuePointName=None, params=None, _id: _ESId = None):
        if _id is None:
            comment = repr(comment)
            chapter = "undefined" if chapter is None else repr(chapter)
            url = "undefined" if url is None else repr(url)
            frameTarget = "undefined" if frameTarget is None else repr(frameTarget)
            cuePointName = "undefined" if cuePointName is None else repr(cuePointName)
            params = "undefined" if params is None else repr(params)

            code = f"new MarkerValue({comment}, {chapter}, {url}, {frameTarget}, {cuePointName}, {params})"
            ret = _executeScript(code)
            _id = _ESId(ret.split(",")[2])

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
    def __init__(self, _id: _ESId = None):
        if _id is None:
            ret = _executeScript("new Shape()")
            _id = _ESId(ret.split(",")[2])

        super().__init__(_id)

class ShapeLayer(ESWrapper):pass
class SolidSource(FootageSource):pass
class System(ESWrapper):pass

class TextDocument(ESWrapper):
    def __init__(self, docText="", _id: _ESId = None):
        if _id is None:
            text = repr(docText)
            ret = _executeScript(f"new TextDocument({text})")
            _id = _ESId(ret.split(",")[2])

        super().__init__(_id)

class TextLayer(AVLayer):pass
class Viewer(ESWrapper):pass
class ViewOptions(ESWrapper):pass
