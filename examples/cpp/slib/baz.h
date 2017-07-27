#pragma once

#ifdef _WIN32
    #ifdef DLL_EXPORT
        #define BAZ_API __declspec(dllexport)
    #else
        #define BAZ_API __declspec(dllimport)
    #endif
#else
    #define BAZ_API
#endif

BAZ_API int ExtractBaz();
