#include "AEConfig.h"
#include "entry.h"

#ifdef AE_OS_WIN
#include <windows.h>
#include <stdio.h>
#include <string.h>
#elif defined AE_OS_MAC
#include <wchar.h>
#endif

#include "AE_GeneralPlug.h"
#include "AE_Effect.h"
#include "A.h"
#include "AE_EffectUI.h"
#include "SPSuites.h"
#include "AE_AdvEffectSuites.h"
#include "AE_EffectCBSuites.h"
#include "AEGP_SuiteHandler.h"
#include "AE_Macros.h"

extern "C" DllExport AEGP_PluginInitFuncPrototype EntryPointFunc;

#include "PythonInstance.h"

#ifdef _DEBUG
#pragma comment(lib, "x64/Debug/dll/AEPython.lib")
#else
#pragma comment(lib, "x64/Release/dll/AEPython.lib")
#endif


static AEGP_Command S_python_cmd = 0;

AEGP_PluginID S_my_id = 0;
SPBasicSuite* sP = 0;

static A_Err UpdateMenuHook(
	AEGP_GlobalRefcon		plugin_refconPV,		/* >> */
	AEGP_UpdateMenuRefcon	refconPV,				/* >> */
	AEGP_WindowType			active_window)			/* >> */
{
	A_Err 				err = A_Err_NONE;
	AEGP_SuiteHandler	suites(sP);

	if (S_python_cmd) {
		err = suites.CommandSuite1()->AEGP_EnableCommand(S_python_cmd);
	}
	return err;
}

static A_Err CommandHook(
	AEGP_GlobalRefcon	plugin_refconPV,		/* >> */
	AEGP_CommandRefcon	refconPV,				/* >> */
	AEGP_Command		command,				/* >> */
	AEGP_HookPriority	hook_priority,			/* >> */
	A_Boolean			already_handledB,		/* >> */
	A_Boolean* handledPB)				/* << */
{
	A_Err 				err = A_Err_NONE;
	AEGP_SuiteHandler	suites(sP);

	*handledPB = FALSE;

	if (command == S_python_cmd) {
		AEPython::showWindow();
		*handledPB = TRUE;
	}
	return err;
}

static std::string GetPluginDir()
{
	auto hModule = GetModuleHandle("AEPython.aex");
	char charPath[_MAX_PATH] = "";
	GetModuleFileName(hModule, charPath, _MAX_PATH);

	std::string strPath = charPath;
	return strPath.substr(0, strPath.find_last_of('\\'));
}

static void InitPython()
{
	auto plugin_dir = GetPluginDir();

	std::string path = getenv("PATH");
	path = plugin_dir + "\\python-3.10.9-embed-amd64;" + path;
	_putenv_s("PATH", path.c_str());

	auto dll = plugin_dir + "\\AEPython.dll";
	LoadLibrary(dll.c_str());

	AEPython::init(S_my_id, sP);
}

A_Err EntryPointFunc(
	struct SPBasicSuite* pica_basicP,			/* >> */
	A_long				 	major_versionL,			/* >> */
	A_long					minor_versionL,			/* >> */
	AEGP_PluginID			aegp_plugin_id,			/* >> */
	AEGP_GlobalRefcon* global_refconP)		/* << */
{
	A_Err 				err = A_Err_NONE;

	S_my_id = aegp_plugin_id;
	sP = pica_basicP;

	AEGP_SuiteHandler	suites(pica_basicP);

	ERR(suites.CommandSuite1()->AEGP_GetUniqueCommand(&S_python_cmd));
	ERR(suites.CommandSuite1()->AEGP_InsertMenuCommand(S_python_cmd, "Python", AEGP_Menu_WINDOW, AEGP_MENU_INSERT_SORTED));
	ERR(suites.RegisterSuite5()->AEGP_RegisterCommandHook(S_my_id, AEGP_HP_BeforeAE, AEGP_Command_ALL, CommandHook, NULL));
	ERR(suites.RegisterSuite5()->AEGP_RegisterUpdateMenuHook(S_my_id, UpdateMenuHook, NULL));

	InitPython();

	return err;
}
