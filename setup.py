from setuptools import setup, find_packages

setup(
    name="anthropic_mock_wrapper",
    version="0.2.3",
    packages=find_packages(),
    install_requires=[
        "anthropic",
        "lorem",
    ],
    extras_require={
        "dev": [
            "mypy",
            "pytest",
            "pytest-asyncio",
        ]
    },
    author="Anurag Angara",
    author_email="anurag.angara@gmail.com",
    description="A lightweight wrapper around the Anthropic Python client for testing purposes",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/ps2-controller/anthropic_mock_wrapper",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
)