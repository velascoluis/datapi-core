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
    packages=find_packages(),
    include_package_data=True,
    install_requires=parse_requirements('requirements.txt'),
    dependency_links=[
        "git+https://github.com/velascoluis/malloy-py.git@main#egg=malloy"
    ],
    entry_points="""
        [console_scripts]
        datapi=datapi.cli:cli
    """,
)
