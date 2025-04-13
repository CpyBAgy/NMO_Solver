from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="nmo_solver",
    version="1.0.0",
    author="Ivan Bashkatov - CpyBAgy",
    author_email="ibaskatov9@gmail.com",
    description="Automated solver for NMO tests on Rosminzdrav portal",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/CpyBAgy/NMO_Solver",
    packages=find_packages(),
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 4 - Beta",
        "Topic :: Education",
        "Topic :: Internet :: WWW/HTTP :: Browsers",
    ],
    python_requires=">=3.7",
    install_requires=[
        "selenium==4.10.0",
        "webdriver-manager>=4.0.0",
        "requests>=2.28.0",
        "beautifulsoup4>=4.12.0",
    ],
    entry_points={
        "console_scripts": [
            "nmo_solver=nmo_solver.main:main",
        ],
    },
)