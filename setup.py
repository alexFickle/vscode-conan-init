from setuptools import setup

setup(name="vscode_conan_init",
      version="0.1",
      description="Sets up vscode for a project that uses conan.",
      author="Alex Fickle",
      license="MIT",
      url="https://github.com/alexFickle/vscode-conan-init",
      scripts=["bin/vscode-conan-init"],
      packages=["vscode_conan_init"])
