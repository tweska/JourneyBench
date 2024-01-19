CPP_COMPILER = g++
CPP_FLAGS = -O3 -Wall -Wextra -std=c++11 -fPIC
CPP_INCLUDES = -I../../include

all: csa_opt.so

%.o: %.cpp
	$(CPP_COMPILER) $(CPP_FLAGS) -c $(CPP_INCLUDES) $< -o $@

csa_opt.so: csa_opt.o
	$(CPP_COMPILER) $(CPP_FLAGS) -shared $(CPP_INCLUDES) $^ -o $@

clean:
	rm -f *.o *.so
