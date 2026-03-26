from setuptools import setup, find_packages

setup(
    name="ai-collab-blackbox",
    version="1.0.0",
    author="A1 Coder",
    description="A unified work logging protocol for multi-AI / multi-thread collaborative development.",
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "ai-blackbox=scripts.cli:main",
        ]
    }
)
