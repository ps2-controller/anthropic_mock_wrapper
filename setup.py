from setuptools import setup, find_packages

setup(
    name="anthropic_mock_wrapper",  # Changed to a new, unique name
    version="0.2.1",
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
    author="Your Name",
    author_email="your.email@example.com",
    description="A lightweight wrapper around the Anthropic Python client for testing purposes",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/anthropic_mock_wrapper",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
)