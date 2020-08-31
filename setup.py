import sys
from setuptools import setup, find_packages

if sys.version_info < (3, 6):
    raise ValueError("Requires Python 3.6 or superior")

install_requires = ["quart", "requests"]
description = ""


classifiers = [
    "Programming Language :: Python",
    "License :: OSI Approved :: Apache Software License",
    "Development Status :: 5 - Production/Stable",
    "Programming Language :: Python :: 3 :: Only",
]


setup(
    name="webnetem",
    version="0.1",
    url="https://github.com/tarekziade/webnetem",
    packages=find_packages(),
    long_description=description.strip(),
    description=("web app that drives netem"),
    author="Tarek Ziade",
    author_email="tarek@ziade.org",
    include_package_data=True,
    zip_safe=False,
    classifiers=classifiers,
    install_requires=install_requires,
    entry_points="""
    [console_scripts]
    webnetem = webnetem.server:main
    """,
)
