import setuptools

with open("README.md", "r") as fh:
  long_description = fh.read()

packages = setuptools.find_namespace_packages(include=["clarifai*"])

setuptools.setup(
    name="clarifai",
    version="9.7.5",
    author="Clarifai",
    author_email="support@clarifai.com",
    description="Clarifai Python SDK",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Clarifai/clarifai-python",
    packages=packages,
    classifiers=[
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
    license="Apache 2.0",
    python_requires='>=3.8',
    install_requires=[
        "clarifai-grpc>=9.7.3", "tritonclient==2.34.0", "packaging", "tqdm==4.64.1", "rich==13.4.2"
    ],
    entry_points={
        "console_scripts": [
            "clarifai-model-upload-init = clarifai.models.model_serving.cli.repository:model_upload_init",
            "clarifai-triton-zip = clarifai.models.model_serving.cli.model_zip:main",
            "clarifai-upload-model = clarifai.models.model_serving.cli.deploy_cli:main"
        ],
    },
    include_package_data=True)
