#include "PythonInstance.h"
#include "Util.h"

#include "../Libs/pybind11/include/pybind11/embed.h"
#include "../Libs/pybind11/include/pybind11/pybind11.h"

namespace py = pybind11;

std::unique_ptr<py::scoped_interpreter> interpreter;
std::unique_ptr<py::dict> locals;

static AEGP_PluginID S_my_id;
static SPBasicSuite* sP;

static auto getMainHWND()
{
	A_Err err = A_Err_NONE;
	AEGP_SuiteHandler suites(sP);
	uint64 hwnd = 0;
	ERR(suites.UtilitySuite5()->AEGP_GetMainHWND(&hwnd));
	return hwnd;
}

static std::wstring executeScript(std::wstring w_code)
{
	A_Err err = A_Err_NONE;
	AEGP_SuiteHandler suites(sP);

	A_Boolean outAvailablePB = false;
	AEGP_MemHandle outResultPH = 0;
	AEGP_MemHandle outErrorStringPH = 0;

	ERR(suites.UtilitySuite5()->AEGP_IsScriptingAvailable(&outAvailablePB));
	auto code = toString(w_code);
	ERR(suites.UtilitySuite5()->AEGP_ExecuteScript(S_my_id, code.c_str(), true, &outResultPH, &outErrorStringPH));

	A_char* res = NULL;
	ERR(suites.MemorySuite1()->AEGP_LockMemHandle(outResultPH, reinterpret_cast<void**>(&res)));
	std::wstring strRes = toWString(res);

	A_char* error = NULL;
	ERR(suites.MemorySuite1()->AEGP_LockMemHandle(outErrorStringPH, reinterpret_cast<void**>(&error)));
	std::string strErr = error;

	ERR(suites.MemorySuite1()->AEGP_FreeMemHandle(outResultPH));
	ERR(suites.MemorySuite1()->AEGP_FreeMemHandle(outErrorStringPH));

	if (strErr.empty() == false)
	{
		py::exec("raise Exception('ExecuteScriptError')");
	}

	return strRes;
}

static std::wstring getPluginPath()
{
	auto hModule = GetModuleHandle("AEPython.aex");
	wchar_t path[_MAX_PATH] = L"";
	GetModuleFileNameW(hModule, path, _MAX_PATH);
	return path;
}

static void startUndoGroup(std::wstring wname)
{
	A_Err err = A_Err_NONE;
	AEGP_SuiteHandler suites(sP);
	auto name = toString(wname);
	ERR(suites.UtilitySuite1()->AEGP_StartUndoGroup(name.c_str()));
}

static void endUndoGroup()
{
	A_Err err = A_Err_NONE;
	AEGP_SuiteHandler suites(sP);
	ERR(suites.UtilitySuite1()->AEGP_EndUndoGroup());
}

#define PY_CLASS(m, name) py::class_<name>(m, #name)
#define PY_SUB_CLASS(m, name, base_name) py::class_<name, base_name>(m, #name)

PYBIND11_EMBEDDED_MODULE(_AEPython, m) {
	m.def("executeScript", executeScript);
	m.def("getPluginPath", getPluginPath);
	m.def("getMainHWND", getMainHWND);
	m.def("startUndoGroup", startUndoGroup);
	m.def("endUndoGroup", endUndoGroup);
}

void AEPython::init(AEGP_PluginID _my_id, SPBasicSuite* _sP)
{
	S_my_id = _my_id;
	sP = _sP;

	interpreter = std::make_unique< py::scoped_interpreter>();
	locals = std::make_unique< py::dict>();
	py::module_::import("_AEPython").add_object("locals", *locals);

	exec(u8R"(
import sys
import os
import _AEPython

sys.path.append(os.path.dirname(_AEPython.getPluginPath()))
import AEPython as ae
import qtae
)");
}

void AEPython::exec(const std::string& utf8_code)
{
	try
	{
		py::exec(utf8_code, py::globals(), *locals);
	}
	catch (py::error_already_set& e)
	{
		try
		{
			py::print(e.what(), py::arg("file") = py::module_::import("sys").attr("stderr"));
		}
#pragma warning(push)
#pragma warning(disable:4101)
		catch (py::error_already_set& _)
		{
			std::string msg = "Python error.\n";
			msg += e.what();
			AEGP_SuiteHandler suites(sP);
			suites.UtilitySuite5()->AEGP_ReportInfo(S_my_id, msg.c_str());
		}
#pragma warning(pop)
	}
}

void AEPython::showWindow()
{
	exec(u8R"(
import qtae
qtae.ShowPythonWindow()
)");
}
