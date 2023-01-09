#include "Util.h"

std::string toString(const std::wstring& wstr, UINT CodePage)
{
	if (wstr.empty()) return std::string();
	const int size_needed = WideCharToMultiByte(CodePage, 0, &wstr[0], (int)wstr.size(), NULL, 0, NULL, NULL);
	std::string dst(size_needed, 0);
	WideCharToMultiByte(CodePage, 0, &wstr[0], (int)wstr.size(), &dst[0], size_needed, NULL, NULL);
	return dst;
}

std::wstring toWString(const std::string& str, UINT CodePage)
{
	if (str.empty()) return std::wstring();
	const int size_needed = MultiByteToWideChar(CodePage, 0, &str[0], (int)str.size(), NULL, 0);
	std::wstring dst(size_needed, 0);
	MultiByteToWideChar(CodePage, 0, &str[0], (int)str.size(), &dst[0], size_needed);
	return dst;
}
