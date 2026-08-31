#include "../Libs/ExtendScript-Toolkit/SoSharedLibDefs.h"
#include "../Libs/ExtendScript-Toolkit/SoCClient.h"

#include "PythonInstance.h"

#define DllExport extern "C" __declspec( dllexport )

SoServerInterface* gpServer = nullptr;

static char* stringToCharP(const std::string& src)
{
	const auto length = src.length() + 1;
	char* dst = new char[length];
	strcpy_s(dst, length, src.c_str());

	return dst;
}

// Python.exec("Python code string");
DllExport long _exec(TaggedData* argv, long argc, TaggedData* retval)
{
	if (argc != 2 || argv[0].type != kTypeString || argv[1].type != kTypeString)
	{
		return kESErrBadArgumentList;
	}

	const bool success = AEPython::exec(reinterpret_cast<char8_t*>(argv[0].data.string), argv[1].data.string);

	retval->type = kTypeUndefined;

	return success ? kESErrOK : kESErrEval;
}

// Python.eval("Python code string");
DllExport long _eval(TaggedData* argv, long argc, TaggedData* retval)
{
	if (argc != 2 || argv[0].type != kTypeString || argv[1].type != kTypeString)
	{
		return kESErrBadArgumentList;
	}

	auto code = argv[0].data.string;
	auto stack = argv[1].data.string;
	std::string ret = AEPython::eval(reinterpret_cast<char8_t*>(code), stack);

	if (ret.length() == 0)
	{
		return kESErrEval;
	}
	else
	{
		retval->data.string = stringToCharP(ret);
		retval->type = kTypeScript;
		return kESErrOK;
	}
}

DllExport void ESFreeMem(void* p)
{
	delete(char*)(p);
}

DllExport long ESGetVersion()
{
	return 2;
}


DllExport char* ESInitialize(const TaggedData** argv, long argc)
{
	static char ESInitializeFunctions[] = "_exec_ss, _eval_ss";
	return ESInitializeFunctions;
}

DllExport void ESTerminate()
{
}

DllExport void* ESMallocMem(size_t nBytes)
{
	return malloc(nBytes);
}

ESerror_t PyObjectBase_initialize(SoHObject hObject, int argc, TaggedData* argv)
{
	if (argc == 1 && argv[0].type == kTypeInteger)
	{
		auto* id = new long(argv[0].data.intval);
		gpServer->setClientData(hObject, id);
		return kESErrOK;
	}
	else
	{
		gpServer->setClientData(hObject, nullptr);
		return kESErrBadArgumentList;
	}
}

ESerror_t PyObjectBase_finalize(SoHObject hObject)
{
	long* id;
	gpServer->getClientData(hObject, (void**)&id);

	if (id != nullptr)
	{
		AEPython::del_py_object(*id);
		delete id;
	}

	return kESErrOK;
}

SoObjectInterface objectInterface =
{
	PyObjectBase_initialize,
	nullptr, // pull
	nullptr, // get
	nullptr, // call
	nullptr, // valueOf
	nullptr, // toString
	PyObjectBase_finalize
};

DllExport int  ESClientInterface(SoCClient_e kReason, SoServerInterface* pServer, SoHServer hServer)
{
	if (kReason == kSoCClient_init)
	{
		char className[] = "AEPython_PyObjectBase";
		gpServer = pServer;
		gpServer->addClass(hServer, className, &objectInterface);
	}

	return 0;
}
