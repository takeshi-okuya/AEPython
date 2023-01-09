#pragma once
#include "AEConfig.h"

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

#include <string>

std::string toString(const std::wstring& wstr, UINT CodePage = CP_ACP);
std::wstring toWString(const std::string& str, UINT CodePage = CP_ACP);
