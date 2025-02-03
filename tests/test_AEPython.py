import unittest

from AEPython import ae

class TestAEPython(unittest.TestCase):
    def test_dict(self):
        src = {"int":999,
               "float":3.14,
               "bool":True,
               "str":"hello",
               "list":[1,2,3],
               "dict":{"a":1,"b":2,"c":3},
               "none":None,
               "comp": ae.app.project.items.addComp("TestComp", 1920, 1080, 1, 10, 24)
               }

        self.assertEqual(type(src["comp"]), ae.CompItem)

        code = '''
            __temp__ = function(src) {
                dst = {};

                var builtins = Python.import("builtins");
                var keys = builtins.callattr("list", [src.callattr("keys")]);
                var len_keys = keys.callattr("__len__"); 

                for (var i=0; i<len_keys; ++i) { 
                    var key = keys.getitem(i);
                    dst[key] = src.getitem(key);
                }
                
                return dst;
            }'''
        func = ae.executeScript(code)

        dst = func(src)
        self.assertEqual(type(dst), ae.ESWrapper)

        for key in src:
            self.assertEqual(src[key], getattr(dst, key))


unittest.TextTestRunner().run(unittest.TestLoader().loadTestsFromTestCase(TestAEPython))
