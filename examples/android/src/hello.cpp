#include <pthread.h>
#include <unistd.h>
#include <fcntl.h>
#include <stdint.h>

#include <android/native_activity.h>
#include <android/looper.h>

#include <stdio.h>
#include <stdlib.h>

#include <EGL/egl.h>
#include <GLES2/gl2.h>
#include <GLES2/gl2ext.h>

#include "base.h"
#include "utils.h"
#include "platform/graphics.h"

int32 _pipe_read;
int32 _pipe_write;
AInputQueue* _queue;
ALooper* _looper;
EGLSurface _surface;
EGLDisplay _display;
EGLint _w;
EGLint _h;

enum MessageType {
    START,
    RESUME,
    PAUSE,
    STOP,
    DESTROY,
    FOCUSED,
    UNFOCUSED,
    WINDOW_CREATED,
    WINDOW_RESIZED,
    WINDOW_DESTROYED,
    INPUT_QUEUE_CREATED,
    INPUT_QUEUE_DESTROYED
};


class Message {
public:
    MessageType type;
    void* data;
};


enum Identifier {
    MESSAGE,
    INPUT
};


void printGLString(const char *name, GLenum s) {
    const char *v = (const char *) glGetString(s);
    LOGI("GL %s = %s\n", name, v);
}


int u_MVPMatrix_h;
int a_Position_h;
int a_Color_h;


void windowCreated(ANativeWindow *window) {
    const EGLint attribs[] = {
            EGL_SURFACE_TYPE, EGL_WINDOW_BIT,
            EGL_RENDERABLE_TYPE, EGL_OPENGL_ES2_BIT,
            EGL_BLUE_SIZE, 8,
            EGL_GREEN_SIZE, 8,
            EGL_RED_SIZE, 8,
            EGL_NONE
    };
    EGLint format;
    EGLint numConfigs;
    EGLConfig config;
    EGLContext context;

    _display = eglGetDisplay(EGL_DEFAULT_DISPLAY);

    eglInitialize(_display, 0, 0);

    /* Here, the application chooses the configuration it desires.
     * find the best match if possible, otherwise use the very first one
     */
    eglChooseConfig(_display, attribs, nullptr,0, &numConfigs);
    EGLConfig* supportedConfigs(new EGLConfig[numConfigs]); // memory leak?
    //assert(supportedConfigs);
    eglChooseConfig(_display, attribs, supportedConfigs, numConfigs, &numConfigs);
    //assert(numConfigs);
    auto i = 0;
    for (; i < numConfigs; i++) {
        auto& cfg = supportedConfigs[i];
        EGLint r, g, b, d;
        if (eglGetConfigAttrib(_display, cfg, EGL_RED_SIZE, &r)   &&
            eglGetConfigAttrib(_display, cfg, EGL_GREEN_SIZE, &g) &&
            eglGetConfigAttrib(_display, cfg, EGL_BLUE_SIZE, &b)  &&
            eglGetConfigAttrib(_display, cfg, EGL_DEPTH_SIZE, &d) &&
            r == 8 && g == 8 && b == 8 && d == 0 ) {

            config = supportedConfigs[i];
            break;
        }
    }
    if (i == numConfigs) {
        config = supportedConfigs[0];
    }

    /* EGL_NATIVE_VISUAL_ID is an attribute of the EGLConfig that is
     * guaranteed to be accepted by ANativeWindow_setBuffersGeometry().
     * As soon as we picked a EGLConfig, we can safely reconfigure the
     * ANativeWindow buffers to match, using EGL_NATIVE_VISUAL_ID. */
    eglGetConfigAttrib(_display, config, EGL_NATIVE_VISUAL_ID, &format);
    _surface = eglCreateWindowSurface(_display, config, window, NULL);
    context = eglCreateContext(_display, config, NULL, NULL);

    if (eglMakeCurrent(_display, _surface, _surface, context) == EGL_FALSE) {
        LOGW("Unable to eglMakeCurrent");
        return;
    }

    eglQuerySurface(_display, _surface, EGL_WIDTH, &_w);
    eglQuerySurface(_display, _surface, EGL_HEIGHT, &_h);

    printGLString("VENDOR", GL_VENDOR);
    printGLString("RENDERER", GL_RENDERER);
    printGLString("VERSION", GL_VERSION);
    printGLString("EXTENSIONS", GL_EXTENSIONS);

//    glViewport(0, 0, _w, _h);
    glClearColor(0.5f, 0.5f, 0.5f, 1.0f);
    checkGlError("glClearColor");
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT);
    checkGlError("glClear");

    LOGI("w: %d, h: %d", _w, _h);

    if (!eglSwapBuffers(_display, _surface)) {
        LOGE("eglSwapBuffers() returned error %d", eglGetError());
    }

    const char* vs = \
    "uniform mat4 u_MVPMatrix;"
    ""
    "attribute vec4 a_Color;"
    "attribute vec4 a_Position;"
    ""
    "varying vec4 v_Color;"
    ""
    "void main() {"
    "   v_Color = a_Color;"
    "   gl_Position = u_MVPMatrix * a_Position;"
    "   gl_Position = vec4(gl_Position.x, gl_Position.y, 0.0, 1.0);"
    "}";

    const char* fs = \
    "precision mediump float;"
    ""
    "varying vec4 v_Color;"
    ""
    "void main() {"
    "   gl_FragColor = vec4(1.0, 1.0, 1.0, 1.0);"
    "}";

    int vsh = makeShader(GL_VERTEX_SHADER, vs);
    int fsh = makeShader(GL_FRAGMENT_SHADER, fs);

    int ph = G::CreateProgram();
    glAttachShader(ph, vsh);
    glAttachShader(ph, fsh);
//    glBindAttribLocation(ph, 0, "a_Position");
//    checkGlError("glBindAttributLocation 0");
//    glBindAttribLocation(ph, 1, "a_Color");
//    checkGlError("glBindAttributLocation 1");
    glLinkProgram(ph);
    int status = 666;
    glGetProgramiv(ph, GL_LINK_STATUS, &status);

    if (status == GL_TRUE) {
        LOGI("shader linkage succeeded");
    } else {
        GLint size = 0;
        glGetProgramiv(ph, GL_INFO_LOG_LENGTH, &size);
        GLchar* message = new GLchar[size];
        glGetProgramInfoLog(ph, size, nullptr, message);
        LOGE("SHADER LINKAGE FAILED: %s", message);
    }

    u_MVPMatrix_h = glGetUniformLocation(ph, "u_MVPMatrix");
    a_Position_h = glGetAttribLocation(ph, "a_Position");
    a_Color_h = glGetAttribLocation(ph, "a_Color");

    LOGW("u_MVPMatrix_h = %d", u_MVPMatrix_h);
    LOGW("a_Position_h = %d", a_Position_h);
    LOGW("a_Color_h = %d", a_Color_h);
    LOGW("ph = %d", ph);

    glUseProgram(ph);



//    if (!eglSwapBuffers(_display, _surface)) {
//        LOGE("eglSwapBuffers() returned error %d", eglGetError());
//    }

    //glViewport(0, 0, w, h);
    //checkGlError("glViewport");
}



void processMessages() {
    Message message;

    int32 res = read(_pipe_read, &message, sizeof(message));
    if (res == sizeof(message)) {
        switch (message.type) {
            case MessageType::INPUT_QUEUE_CREATED:
                LOGI("Input queue created.");
                _queue = static_cast<AInputQueue*>(message.data);
                AInputQueue_attachLooper(_queue, _looper, Identifier::INPUT, nullptr, nullptr);
                break;
            case MessageType::WINDOW_CREATED:
                LOGI("Window created.");
                windowCreated(static_cast<ANativeWindow*>(message.data));
                break;
            case MessageType::FOCUSED:
                LOGI("Window focused.");
                break;
            case MessageType::UNFOCUSED:
                LOGI("Window unfocused.");
                break;
            default:
                LOGW("Unknown message type");
                break;
        }
    } else if (res > 0) {
        LOGF("BAD MESSAGE!");
    }
}

void processInputs() {
    AInputEvent* event = nullptr;
    if (AInputQueue_getEvent(_queue, &event) >= 0) {
        LOGV("New input event: type=%d\n", AInputEvent_getType(event));
        if (AInputQueue_preDispatchEvent(_queue, event)) {
            LOGV("Input was consumed by pre-dispatch.");
        } else {
            if (AInputEvent_getType(event) == AINPUT_EVENT_TYPE_MOTION) {
                //int pointer_index = AMotionEvent_getPointerCount(event);
                int pointer_index = 0;
                float x = AMotionEvent_getX(event, pointer_index);
                float y = AMotionEvent_getY(event, pointer_index);
                LOGV("MOTION -- X: %f -- Y: %f", x, y);

                if (x != 0.f && y != 0.f) {
                    float red = x / _w;
                    float green = y / _h;
                    float blue = 1 - red - green;

                    glClearColor(red, green, blue, 1.0f);
                    checkGlError("glClearColor");
                    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT);
                    checkGlError("glClear");
                }
            }
            LOGV("Finishing input.");
            AInputQueue_finishEvent(_queue, event, 1);
        }
    }

    #define R (((rand()%100)-50)*0.5f)


    checkGlError("pre setup");
    for (int i=0; i < 1000; i++) {
//    float positions[3*3] = {
//        0.0, 0.5, 0.0,
//        -0.5, -0.5, 0.0,
//        0.5, -0.5, 0.0,
//    };
    float positions[3*3] = {
        R, R, R,
        R, R, R,
        R, R, R,
    };
    glVertexAttribPointer(a_Position_h, 3, GL_FLOAT, GL_FALSE, 0, positions);
    checkGlError("glVertexAttribPointer 1");
    glEnableVertexAttribArray(a_Position_h);
    checkGlError("glEnableVertexAttribArray 1");

    float colors[12] = {
        0.5, 0.2, 0.8, 0.9,
        0.2, 0.3, 0.6, 0.6,
        0.8, 0.4, 0.9, 0.4
    };
             // a_Color_h \/
    glVertexAttribPointer(0, 4, GL_FLOAT, GL_FALSE, 0, colors);
    checkGlError("glVertexAttribPointer 2");
    // LOGE("%d", a_Color_h);
    glEnableVertexAttribArray(0); // a_Color_h
    checkGlError("glEnableVertexAttribArray 2");

    float matrix[4*4] = {
        1.0, 0.0, 0.0, 0.0,
        0.0, 1.0, 0.0, 0.0,
        0.0, 0.0, 1.0, 0.0,
        0.0, 0.0, 0.0, 1.0
    };
    glUniformMatrix4fv(u_MVPMatrix_h, 1, GL_FALSE, matrix);
    checkGlError("glUniformMatrix4fv");

    checkGlError("pre glDrawArrays");
    glDrawArrays(GL_TRIANGLES, 0, 3);
    checkGlError("glDrawArrays");

    }

    if (!eglSwapBuffers(_display, _surface)) {
        LOGE("eglSwapBuffers() returned error %d", eglGetError());
    }
}


void* entry(void*) {
    LOGI("Thread started.");

    _looper = ALooper_prepare(ALOOPER_PREPARE_ALLOW_NON_CALLBACKS);
    ALooper_addFd(_looper, _pipe_read, Identifier::MESSAGE, ALOOPER_EVENT_INPUT, nullptr, nullptr);

    int events;
    int ident;

    while (true) {
        ident = ALooper_pollOnce(0, nullptr, &events, nullptr);
        if (ident == Identifier::MESSAGE) {
            processMessages();
        } else if (ident == Identifier::INPUT) {
            processInputs();
        }
    }
};


void sendMessage(MessageType type, void *data) {
    Message message;
    message.type = type;
    message.data = data;
    if (write(_pipe_write, &message, sizeof(message)) != sizeof(message)) {
        LOGF("Failure writing to pipe: %s", strerror(errno));
    }
}


void onInputQueueCreated(ANativeActivity* activity, AInputQueue* queue) {
    sendMessage(MessageType::INPUT_QUEUE_CREATED, queue);
}

void onWindowFocusChanged(ANativeActivity* activity, int focused) {
    sendMessage(focused ? MessageType::FOCUSED : MessageType::UNFOCUSED, nullptr);
}

void onNativeWindowCreated(ANativeActivity* activity, ANativeWindow* window) {
    sendMessage(MessageType::WINDOW_CREATED, window);
}

extern "C" void android_main(ANativeActivity* activity, void* savedState, size_t savedStateSize)
{
    LOGI("Initialising...");

    int32 pipes[2];
    if (pipe(pipes)) {
        LOGF("Could not create pipe: %s", strerror(errno));
        return;
    }
    _pipe_read = pipes[0];
    _pipe_write = pipes[1];
    fcntl(_pipe_read, F_SETFL, O_NONBLOCK);

    //activity->callbacks->onDestroy = onDestroy;
    //activity->callbacks->onStart = onStart;
    // activity->callbacks->onResume = onResume;
    // activity->callbacks->onPause = onPause;
    //activity->callbacks->onStop = onStop;
    activity->callbacks->onWindowFocusChanged = onWindowFocusChanged;
    activity->callbacks->onNativeWindowCreated = onNativeWindowCreated;
    //activity->callbacks->onNativeWindowDestroyed = onNativeWindowDestroyed;
    activity->callbacks->onInputQueueCreated = onInputQueueCreated;
    //activity->callbacks->onInputQueueDestroyed = onInputQueueDestroyed;

    LOGV("Creating thread.");
    pthread_attr_t attr;
    pthread_attr_init(&attr);
    pthread_attr_setdetachstate(&attr, PTHREAD_CREATE_DETACHED);
    pthread_t thread;
    pthread_create(&thread, &attr, entry, nullptr);
    LOGV("Thread creation done. Returning.");
}


