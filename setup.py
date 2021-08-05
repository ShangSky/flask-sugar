# coding = utf-8
import re
from setuptools import setup, find_packages

with open("flask_sugar/__init__.py", "r") as f:
    version = re.search(
        r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]', f.read(), re.MULTILINE
    ).group(1)
with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="flask-sugar",
    python_requires=">=3.6",
    version=version,
    description="Flask Sugar is a web framework for building APIs with Flask, Pydantic and Python 3.6+ type hints.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="shangsky",
    author_email="t_c_y@outlook.com",
    maintainer="shangsky",
    maintainer_email="t_c_y@outlook.com",
    license="MIT",
    packages=find_packages(),
    platforms=["all"],
    url="https://github.com/shangsky/flask-sugar",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Operating System :: OS Independent",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Topic :: Software Development :: Libraries",
    ],
    install_requires=["flask>=2.0", "pydantic>=1.8,<2.0.0"],
)
