from setuptools import find_packages, setup

setup(
    name="gdrive_suite",
    version="0.1.0",
    author="Orlando Reyes",
    author_email="eorlando.reyesruiz@gmail.com",
    description="A client for interacting with Google Drive and Google Sheets",
    long_description=open("README.md").read(),
    url="https://github.com/TheLionCoder/cloud-utils",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.11",
    install_requires=[
        "google-api-python-client",
        "google-auth-httplib2",
        "gogole-auth-ouathlib",
        "loguru",
        "pyyaml",
    ],
    extra_require={
        "dev": [
            "mypy",
            "pytest-mock",
        ]
    },
)
