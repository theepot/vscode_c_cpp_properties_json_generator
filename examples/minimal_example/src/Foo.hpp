#pragma once

#include <iostream>


class Foo
{
public:
    static inline void sayHello()
    {
        std::cout << "Hello from Foo :)\n";
    }
};
