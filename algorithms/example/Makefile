CPP_COMPILER = g++
CPP_FLAGS = -O3 -Wall -Wextra -std=c++11 -fPIC
CPP_INCLUDES = -I../../include

all: example.so

example.o: example.cpp
	$(CPP_COMPILER) $(CPP_FLAGS) -c $(CPP_INCLUDES) $< -o $@

example.so: example.o
	$(CPP_COMPILER) $(CPP_FLAGS) -shared $(CPP_INCLUDES) $^ -o $@

clean:
	rm -f *.o *.so
