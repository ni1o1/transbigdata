import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()
 
setuptools.setup(
    name="transbigdata",
    version="0.2.0",
    author="Qing Yu",
    author_email="qingyu0815@foxmail.com",
    description="A tool for transportation big data",
    long_description=long_description,
    long_description_content_type="text/markdown",
    license="BSD",
    url="https://github.com/ni1o1/transbigdata",
    project_urls={
        "Bug Tracker": "https://github.com/ni1o1/transbigdata/issues",
    },
    install_requires=[
        "geopandas","matplotlib","plot_map >= 0.3.3","CoordinatesConverter>=0.1.4"
        ],
    classifiers=[
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Framework :: Matplotlib",
        "Topic :: Text Processing :: Indexing",
        "Topic :: Utilities",
        "Topic :: Internet",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.8",
    ],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.6",
)
