#include "../base.h"

namespace G {

int CreateProgram() {
    int ph = glCreateProgram();
    if (ph == 0) {
        LOGE("glCreateProgram RETURNED 0! PROGRAM CREATION FAILED.");
    }

    return ph;
}

}
