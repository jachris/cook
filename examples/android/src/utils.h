#pragma once

#include <GLES2/gl2.h>
//#include <GLES2/gl2ext.h>

#include "base.h"

int makeShader(GLenum type, const char* source);
int countStringLength(const char* str);
void checkGlError(const char* op);
char const* gl_error_string(GLenum const err);