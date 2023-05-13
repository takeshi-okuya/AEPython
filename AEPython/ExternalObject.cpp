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
DllExport long exec(TaggedData* argv, long argc, TaggedData* retval)
{
	if (argc != 1 || argv[0].type != kTypeString)
	{
		return kESErrBadArgumentList;
	}

	bool success = AEPython::exec(argv[0].data.string);

	retval->type = kTypeUndefined;

	return success ? kESErrOK : kESErrEval;
}

// Python.eval("Python code string");
DllExport long eval(TaggedData* argv, long argc, TaggedData* retval)
{
	if (argc != 1 || argv[0].type != kTypeString)
	{
		return kESErrBadArgumentList;
	}

	std::string ret = AEPython::eval(argv[0].data.string);

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
	return 1;
}

DllExport char* ESInitialize(const TaggedData** argv, long argc)
{
	return "exec_s,eval_a";
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
		gpServer = pServer;
		gpServer->addClass(hServer, "AEPython_PyObjectBase", &objectInterface);
	}

	return 0;
}
