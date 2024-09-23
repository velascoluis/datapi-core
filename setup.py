from setuptools import setup, find_packages


def parse_requirements(filename):
    requirements = []
    with open(filename, 'r') as f:
        for line in f:
            line = line.strip()
            if line.startswith('git+'):
                continue  # Skip git URLs for now
            requirements.append(line)
    return requirements


setup(
    name="datapi",
    version="0.1.0",
    author="dataPi",
    author_email="info@getdapi.com",
    description="dataPi implements a datalakehouse head to get your informational data closer to your applications",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/velascoluis/datapi-core",
    packages=find_packages(),
    package_data={
        "datapi.core": ["templates/*.jinja2"],
    },
    include_package_data=True,
    install_requires=parse_requirements("requirements.txt"),
    dependency_links=[
        "git+https://github.com/velascoluis/malloy-py.git@main#egg=malloy"
    ],
    entry_points="""
        [console_scripts]
        datapi=datapi.cli:cli
    """,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
