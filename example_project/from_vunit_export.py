"""
Create a vhdl_ls.toml file from a VUnit --export-json file
"""

import argparse
import json
import toml
from os.path import relpath, dirname, join
from glob import glob


def main():
    parser = argparse.ArgumentParser("Create a vhdl_ls.toml file from a VUnit --export-json file")
    parser.add_argument("json_file", nargs=1,
                        help="The input .json file")
    parser.add_argument("-o", "--output", default="vhdl_ls.toml",
                        help="The output vhdl_ls.toml file")
    parser.add_argument("-g", "--ghdl-lib", default="lib",
                        help="Which lib to use for ghdl-ls")

    args = parser.parse_args()

    with open(args.json_file[0], "r") as fptr:
        data = json.load(fptr)

    libraries = {}
    hdl_checker = {'sources': []}
    ghdl = {'options': {'ghdl_analysis': ["--std=08"]}, 'files': []}
    for source_file in data["files"]:
        file_name = source_file["file_name"]
        library_name = source_file["library_name"]

        if not library_name in libraries:
            libraries[library_name] = set()
            ghdl['options']['ghdl_analysis'].append("-Pvunit_out/ghdl/libraries/{}".format(library_name))

        libraries[library_name].add(file_name)
        hdl_checker['sources'].append([file_name, {'library': library_name, 'flags': ["--std=08"]}])
        if library_name == args.ghdl_lib:
            ghdl['files'].append({"file": file_name, "language": "vhdl"})

    with open(args.output, "w") as fptr:
        for key in libraries:
            libraries[key] = dict(files=[relpath(file_name, dirname(args.output))
                                         for file_name in libraries[key]])
        toml.dump(dict(libraries=libraries), fptr)

    with open(".hdl_checker.config", "w") as outfile:
        json.dump(hdl_checker, outfile, indent=4)

    with open("hdl-prj.json", "w") as outfile:
        json.dump(ghdl, outfile, indent=4)
        

if __name__ == "__main__":
    main()
