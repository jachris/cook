#include <iostream>

#include "main.h"

#include "bar.h"
#include "baz.h"

using std::cout;
using std::endl;

int main()
{
    cout << "HELLO_WORLD = " << HELLO_WORLD << endl;
    cout << "Foo = " << FOO << endl;
    cout << "Bar::DoBar() = " << Bar::DoBar() << endl;
    cout << "ExtractBaz() = " << ExtractBaz() << endl;
}
