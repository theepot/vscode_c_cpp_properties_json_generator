VSCODE_CONFIG_DIR := .vscode
VSCODE_C_CPP_PROPERTIES_FILE := $(VSCODE_CONFIG_DIR)/c_cpp_properties.json

CXXFLAGS := -Isrc

.PHONY: all
all:
	$(CXX) -o hello $(CXXFLAGS) src/*.cpp $(LFLAGS)

.PHONY: vscode_c_cpp_properties
vscode_c_cpp_properties:
	mkdir -p $(VSCODE_CONFIG_DIR)
	gen_vscode_c_cpp_properties_json.py \
		--output=$(VSCODE_C_CPP_PROPERTIES_FILE) \
		--cc=$(shell which $(CC)) \
		--cxx=$(shell which $(CXX)) \
		--cflags="$(CFLAGS)" \
		--cxxflags="$(CXXFLAGS)"

