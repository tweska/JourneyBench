CPP_COMPILER = g++
CPP_FLAGS = -O3 -Wall -Wextra -std=c++11 -fPIC
CPP_INCLUDES = -I../../include

TARGET = $(notdir $(patsubst %/,%,$(dir $(abspath $(lastword $(MAKEFILE_LIST)))))).so

all: $(TARGET)

%.o: %.cpp
	$(CPP_COMPILER) $(CPP_FLAGS) -c $(CPP_INCLUDES) $< -o $@

%.so: %.o
	$(CPP_COMPILER) $(CPP_FLAGS) -shared $(CPP_INCLUDES) $^ -o $@

clean:
	rm -f *.o *.so
