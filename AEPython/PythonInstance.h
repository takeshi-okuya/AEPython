#pragma once
#include <string>
#include <AE_GeneralPlug.h>

namespace AEPython
{
	__declspec(dllexport) void init(AEGP_PluginID _my_id, SPBasicSuite* _sP);
	__declspec(dllexport) bool exec(const std::string& utf8_code, const std::string& esStack);
	__declspec(dllexport) std::string eval(const std::string& utf8_code, const std::string& esStack);
	__declspec(dllexport) void del_py_object(const long id);
	__declspec(dllexport) void showWindow();
}
