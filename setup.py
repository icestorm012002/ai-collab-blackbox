import os
from setuptools import setup, find_packages

with open(os.path.join(os.path.dirname(__file__), "README.md"), encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="ai-collab-blackbox",
    version="1.1.0",
    author="A1 Coder",
    description="Project skill plus global CLI for multi-AI collaborative work logging.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/icestorm012002/ai-collab-blackbox",
    license="MIT-0",
    packages=find_packages(),
    include_package_data=True,
    package_data={
        "ai_collab_blackbox": ["resources/*", "resources/references/*"],
    },
    entry_points={
        "console_scripts": [
            "ai-blackbox=ai_collab_blackbox.cli:main",
        ]
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.8',
)
