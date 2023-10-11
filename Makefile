PYTHON = env/bin/python
PYTHON_VERSION = $(shell $(PYTHON) -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")

PYBIND_EXTENSION = $(shell python$(PYTHON_VERSION)-config --extension-suffix)
PYBIND_INCLUDES = $(shell $(PYTHON) -m pybind11 --includes)

CPP_COMPILER = g++
CPP_INCLUDES = -Iinclude $(PYBIND_INCLUDES)
CPP_FLAGS = -O3 -Wall -Wextra -std=c++11 -fPIC

CORE_OBJECTS = $(patsubst %.cpp,%.o,$(wildcard benchmark/core/*.cpp))
CORE_MODULE = benchmark/benchmark_core$(PYBIND_EXTENSION)
PROTOC_GENERATED = $(patsubst protobuf/%.proto,benchmark/%_pb2.py,$(wildcard protobuf/*.proto))


all: $(CORE_MODULE) $(PROTOC_GENERATED)

$(CORE_MODULE): $(CORE_OBJECTS)
	$(CPP_COMPILER) $(CPP_FLAGS) -shared $^ $(CPP_INCLUDES) -o $@

benchmark/core/%.o: benchmark/core/%.cpp
	$(CPP_COMPILER) $(CPP_FLAGS) -c $< $(CPP_INCLUDES) -o $@

benchmark/%_pb2.py: protobuf/%.proto
	protoc -I=$(dir $<) --python_out=$(dir $@) $<

clean:
	rm -f $(CORE_OBJECTS) $(CORE_MODULE) $(PROTOC_GENERATED)


.PHONY: all clean
