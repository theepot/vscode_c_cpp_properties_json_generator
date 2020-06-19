#!/usr/bin/env python3

import argparse
import sys
import re
import json
import shlex
import os


PROGRAM_DESCRIPTION = """
TODO program description :(
"""

VSCODE_C_CPP_PROPERTIES_VERSION = 4


GCC_C_STANDARD_TRANSLATION_TABLE = {
    "gnu99": "c99"
}


def main():
    args = parse_args()

    json_root = generate_json(args)

    try:
        with open(args.output, "w") as f:
            json.dump(json_root, f, indent=4)
    except IOError as ex:
        eprint(f"Error while writing output JSON file: {ex}")



def parse_args():
    argParser = argparse.ArgumentParser(description=PROGRAM_DESCRIPTION)

    # argument descriptions
    argParser.add_argument("--cc", help="C Compiler command")
    argParser.add_argument("--cxx", help="C++ Compiler command")

    argParser.add_argument("--cflags", help="C Compiler flags")
    argParser.add_argument("--cxxflags", help="C++ Compiler flags")

    argParser.add_argument("--output", help="Output path to c_cpp_properties.json file")

    # parse
    args =  argParser.parse_args()

    # some checking
    def mandatory(cmd):
        if vars(args)[cmd] is None:
            eprint(f"Error: --{cmd} is manfatory.")
            exit(1)

    mandatory("cc")
    mandatory("cxx")

    mandatory("cflags")
    mandatory("cxxflags")

    mandatory("output")

    # return
    return args


def generate_json(args):
    configuration = {}

    def set_config(key, value):
        if value is not None:
            configuration[key] = value

    # apparently clang-x64 is the only non-MSVC option here.
    configuration["intelliSenseMode"] = "clang-x64"

    # need this at least for include handling by intellisense.
    configuration["compilerPath"] = args.cxx

    # args.cflags and args.cxxflags are actually argument-lists to the compiler.
    # to split these like a shell would when they're passed to c/c++ compilers, we use shlex
    cflags = shlex.split(args.cflags)
    cxxflags = shlex.split(args.cxxflags)
    combined_compiler_flags = cflags + cxxflags
    
    # `name` is always Linux for now, should be platform dependent.
    configuration["name"] = "Linux"

    # TODO should set `intelliSenseMode` here, but will leave on default for now.
    # should depend on the --cc / --cxx parameters really.

    # set includePath depending on -I options to the compiler.
    includes = find_includes(combined_compiler_flags)
    configuration["includePath"] = includes

    # set `defines` depending on -D options to the compiler.
    defines = find_defines(combined_compiler_flags)
    configuration["defines"] = defines

    # TODO should set forcedInclude, but will skip for now.

    # set `compilerPath` depending on -std options.
    # TODO not sure if any translating is needed, just copying as-is for now.
    #      started translating some GCC names to names understandable by vscode (eg gnu99 -> c99)
    set_config("cStandard", c_standard_from_gcc_std_arg(find_standard(cflags)))
    set_config("cppStandard", find_standard(cxxflags))

    # set `configuration`:
    # the 'browse.path` property contains header search paths for intellisense(?)
    # `limitSymbolsToIncludedHeaders` limits intellisense search only to symbols in headers (so no indirect inclusion I think that means).
    # other sources say that intellisense never does that anyway. in any case, true is the most consistent setting here.
    # some say not setting databaseFilename gives issues, so I'm setting it.
    configuration["browse"] = {
        "path": includes,
        "limitSymbolsToIncludedHeaders": True,
        "databaseFilename": "${workspaceFolder}/.vscode/browse.VC.db"
    }

    # create JSON root object, and return it.
    return {
        "configurations": [ configuration ],
        "version": VSCODE_C_CPP_PROPERTIES_VERSION
    }


def find_standard(flags):
    r = re.compile(r"-std=(.+)")
    for option in flags:    
        m = r.search(option)
        if m is not None:
            return m.group(1)
    return None    


def c_standard_from_gcc_std_arg(original_name):
    name = GCC_C_STANDARD_TRANSLATION_TABLE[original_name]
    if name is None:
        return original_name
    else:
        return name


def find_includes(flags):
    return list(map(
        path_to_workspace_path,
        find_weird_options("-I", flags)))


def find_defines(flags):
    return list(find_weird_options("-D", flags))


def find_weird_options(prefix, flags):
    options = set()

    # find the "-PrefixFlags" variant (no space).
    r = re.compile(f"{prefix}(.+)")
    for option in flags:
        m = r.search(option)
        if m is not None:
            options.add(m.group(1))

    # find the "-Prefix Flags" variant (yes space).
    i = 0
    while i < len(flags):
        if flags[i] == prefix and i+1 < len(flags):
            options.add(flags[i+1])
            i += 2
        else:
            i += 1

    return options


def path_to_workspace_path(path):
    if os.path.isabs(path):
        return path
    else:
        return os.path.join("${workspaceFolder}/", path)


def eprint(s):
    print(s, file=sys.stderr)


if __name__ == "__main__":
    main()