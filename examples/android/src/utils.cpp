#include "utils.h"

int makeShader(GLenum type, const char* source) {
    GLuint handle = glCreateShader(type);
    int len = countStringLength(source);
    glShaderSource(handle, 1, &source, &len);
    glCompileShader(handle);

    GLint status = 666;
    glGetShaderiv(handle, GL_COMPILE_STATUS, &status);
    LOGW("received shader status: %d", status);

    if (status == GL_TRUE) {
        LOGI("shader compilation succeeded");
    } else {
        GLint size = 0;
        glGetShaderiv(handle, GL_INFO_LOG_LENGTH, &size);
        GLchar* message = new GLchar[size];
        glGetShaderInfoLog(handle, size, nullptr, message);
        LOGE("SHADER COMPILATION FAILED: %s", message);
        return -1;
    }
    return handle;
}

int countStringLength(const char* str) {
    for (int i=0;; i++) {
        if (str[i] == '\0') {
            return i;
        }
    }
}

void checkGlError(const char* op) {
    for (GLint error = glGetError(); error; error = glGetError()) {
        LOGE("after %s() glError (0x%x) = %s\n", op, error, gl_error_string(error));
    }
}

char const* gl_error_string(GLenum const err)
{
  switch (err)
  {
    // opengl 2 errors (8)
    case GL_NO_ERROR:
      return "GL_NO_ERROR";

    case GL_INVALID_ENUM:
      return "GL_INVALID_ENUM";

    case GL_INVALID_VALUE:
      return "GL_INVALID_VALUE";

    case GL_INVALID_OPERATION:
      return "GL_INVALID_OPERATION";

    /*
    case GL_STACK_OVERFLOW:
      return "GL_STACK_OVERFLOW";

    case GL_STACK_UNDERFLOW:
      return "GL_STACK_UNDERFLOW";
    */

    case GL_OUT_OF_MEMORY:
      return "GL_OUT_OF_MEMORY";

    /*
    case GL_TABLE_TOO_LARGE:
      return "GL_TABLE_TOO_LARGE";
    */

    case GL_INVALID_FRAMEBUFFER_OPERATION:
      return "GL_INVALID_FRAMEBUFFER_OPERATION";

    default:
      return "UNKNOWN_GL_ERROR_CODE";
  }
}
