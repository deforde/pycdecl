from setuptools import setup, find_namespace_packages

setup(
    name="pycdecl",
    version="0.0.0",
    description="Parses c declarations.",
    url="https://github.com/deforde/pycdecl",
    author="Daniel Forde",
    author_email="daniel.forde001@gmail.com",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Parsing",
        "License :: Proprietary",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3 :: Only",
    ],
    packages=find_namespace_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.10, <4",
    install_requires=[
        "pytest",
    ],
    entry_points={
        "console_scripts": [
            "cdecl=cdecl.__main__:main",
        ],
    },
)
