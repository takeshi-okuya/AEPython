#include "../Libs/ExtendScript-Toolkit/SoSharedLibDefs.h"
#include "../Libs/ExtendScript-Toolkit/SoCClient.h"

#include "PythonInstance.h"

#define DllExport extern "C" __declspec( dllexport )

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

	AEPython::exec(argv[0].data.string);

	retval->type = kTypeUndefined;

	return kESErrOK;
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
