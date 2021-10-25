import argparse
import tempfile
import subprocess
import os
import json
import shutil
import platform


def _print_and_run(args):
    """
    Prints a command and runs it.
    Raises an exception if the command fails.

    args: List of arguments.
    """
    print("Running: {}".format(args))
    subprocess.run(args, check=True)


def _install_clang_format():
    """
    Installs clang-format and gets its path.

    Raises an exception on failure.
    """
    with tempfile.TemporaryDirectory() as install_dir:
        _print_and_run([
            "conan", "install", "clang_format/13.0.0@fickle/testing", "-if",
            install_dir, "-g", "json"
        ])
        with open(os.path.join(install_dir,
                               "conanbuildinfo.json")) as info_file:
            info_data = json.load(info_file)
    for dep in info_data["dependencies"]:
        for path in dep["bin_paths"]:
            clang_format = shutil.which("clang-format", path=path)
            if clang_format is not None:
                return clang_format
    raise RuntimeError("Did not find clang-format after installing it.")


def _find_gcc():
    """
    Gets gcc's path.

    Raises an exception if gcc is not on the path.
    gcc should be on the path as this function is only ran
    on Linux. 
    """
    path = shutil.which("gcc")
    if path is None:
        raise RuntimeError("Could not find gcc.  "
                           "This is very odd for a Linux environment.")
    return path


class _MacroDefinitions:
    """
    A collection of macro definitions.

    Ensures that a macro can have only one definition.
    """
    def __init__(self):
        self._dict = {}

    @staticmethod
    def _get_name(definition):
        """
        Gets a macro's name from its definition.
        A macro's definition can be in either the form
        "<name>=<value>" or just "<name>".
        """
        equal_index = definition.find("=")
        if equal_index == -1:
            return definition
        return definition[:equal_index]

    def add(self, definition):
        """
        Adds a macro definition to this collection of definitions.

        Returns the old value of the macro definition.
        Returns None if there was no old value for this definition.
        """
        name = self._get_name(definition)
        old_value = self._dict.get(name)
        self._dict[name] = definition
        return old_value

    def remove(self, name):
        """
        Removes a macro definition by name.

        Returns the old value of the macro definition.
        Returns None if there was no old value for this definition.
        """
        old_value = self._dict.get(name)
        if old_value is not None:
            del self._dict[name]
        return old_value

    def as_list(self):
        """
        Gets all of the defines contained in this collection
        in alphabetical order.
        """
        defines = list(self._dict.values())
        defines.sort()
        return defines


def main():
    """
    Sets up a conan project to be used with vscode
    using command line arguments.

    Returns None on success.
    Raises an exception on failure.
    """
    parser = argparse.ArgumentParser(
        description="Generates a .vscode folder for a project that uses conan."
    )
    parser.add_argument(
        "path",
        help="Directory containing a conanfile.py or conanfile.txt that "
        "will have a .vscode directory generated in.")
    parser.add_argument("-I",
                        "--include",
                        help="Extra include directories.  "
                        "The include directories from the conan dependencies "
                        "of this project are automatically included.  "
                        "This is intended for local include directories.",
                        action="append",
                        default=[])
    parser.add_argument("-D",
                        "--define",
                        help="Extra preprocessor definitions.  "
                        "Is expected to be of either the form "
                        "-D <name>=<value> or -D <name>.  "
                        "Preprocessor defines from conan dependencies of "
                        "this project are automatically imported.  "
                        "Any preprocessor defines given by this command line "
                        "argument will overwrite defines from conan.",
                        action="append",
                        default=[])
    parser.add_argument("-U",
                        "--undefine",
                        help="Removes preprocessor definitions.  "
                        "Can be used to suppress preprocessor defines "
                        "from conan dependencies of this project.",
                        action="append",
                        default=[])
    parser.add_argument("--clang-format",
                        help="Path to clang-format.  "
                        "If not given it will be installed using conan.")
    parser.add_argument("--install-args",
                        help="Arguments that are forwarded to conan install.",
                        nargs=argparse.REMAINDER,
                        action="append",
                        default=[])
    args = parser.parse_args()

    print("Getting information on package's conan dependencies.")
    with tempfile.TemporaryDirectory() as install_dir:
        _print_and_run(
            ["conan", "install", args.path, "-if", install_dir, "-g", "json"] +
            args.install_args)
        with open(os.path.join(install_dir,
                               "conanbuildinfo.json")) as info_file:
            info_data = json.load(info_file)
    macro_defs = _MacroDefinitions()
    includes = [os.path.abspath(x) for x in args.include]
    for dep_info in info_data["dependencies"]:
        includes.extend(dep_info["include_paths"])
        for define in dep_info["defines"]:
            old_value = macro_defs.add(define)
            if old_value is not None and old_value != define:
                raise RuntimeError(
                    'Multiple defines from conan dependencies for '
                    'the same macro: "{}" and "{}"'.format(old_value, define))
    for define in args.define:
        # allowing overwrite without error
        macro_defs.add(define)
    for undefine in args.undefine:
        macro_defs.remove(undefine)

    if args.clang_format is not None:
        clang_format = args.clang_format
    else:
        print("Installing clang-format.")
        clang_format = _install_clang_format()

    vscode_dir = os.path.join(args.path, ".vscode")
    os.makedirs(vscode_dir, exist_ok=True)

    properties_filename = os.path.join(vscode_dir, "c_cpp_properties.json")
    properties = {
        "configurations": [{
            "name": "conan",
            "includePath": includes,
            "defines": macro_defs.as_list(),
        }]
    }
    if platform.system() == "Linux":
        # On my current install of vscode (version 1.61.2)
        # the compiler is defaulted to gcc, but then clang is
        # found and used for the auto-generated compiler path.
        # This generates warnings every time the project is opened.
        # Setting the compiler path to the system gcc suppresses this.
        properties["configurations"][0]["compilerPath"] = _find_gcc()
    with open(properties_filename, "w") as properties_file:
        json.dump(properties, properties_file)
    print("Generated: " + properties_filename)

    settings_filename = os.path.join(vscode_dir, "settings.json")
    settings = {"C_Cpp.clang_format_path": clang_format}
    with open(settings_filename, "w") as settings_file:
        json.dump(settings, settings_file)
    print("Generated: " + settings_filename)
