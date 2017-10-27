#pragma once

#include <android/log.h>

typedef int8_t int8;
typedef int16_t int16;
typedef int32_t int32;
typedef int64_t int64;
typedef uint8_t uint8;
typedef uint16_t uint16;
typedef uint32_t uint32;
typedef uint64_t uint64;

#define LOGV(...) (__android_log_print(ANDROID_LOG_VERBOSE, "MY_TAG", __VA_ARGS__))
#define LOGI(...) (__android_log_print(ANDROID_LOG_INFO, "MY_TAG", __VA_ARGS__))
#define LOGW(...) (__android_log_print(ANDROID_LOG_WARN, "MY_TAG", __VA_ARGS__))
#define LOGE(...) (__android_log_print(ANDROID_LOG_ERROR, "MY_TAG", __VA_ARGS__))
#define LOGF(...) (__android_log_print(ANDROID_LOG_FATAL, "MY_TAG", __VA_ARGS__))

