Contains `vscode-conan-init`: a script for setting up vscode for
a C or C++ project that uses conan for dependency management.

This script only sets up Intellisense and clang-format.
Building is still done as normal through conan's command line.

# Installing

This script is not currently released anywhere.
To install clone and run the below command in the root of this repo.
```sh
$ python3 -m pip install .
```
You can verify that this worked by using
```sh
$ vscode-conan-init --help
```

# Usage

The help message of this tool goes into detail of the command line interface.
The typical usage of this tool is
```sh
# Move to the root of the project you wish to edit using vscode.
$ cd my_project
# Run this script, manually adding any needed local includes and options.
# The below usage shows setting the conan option of coverage to the
# value of lcov.  Can use most arguments to conan install, like options,
# settings, and profiles.
$ vscode-conan-init . -I include -I src --install-args -o coverage=lcov
# now open vscode in your project directory
$ code .
```

# Testing

Most of the testing for this script is manual.
There are some unit tests that can be ran by using the below
command in the root directory of this repo.
```sh
$ python3 -m unittest
```
