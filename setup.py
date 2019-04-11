from setuptools import setup, find_packages

setup(
    name="eForm-Resource",
    version="0.1",
    description="eForm Resource Service",
    author="wzhzzmzzy",
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    extras_require={
        'test': [
            'pytest'
        ]
    }
)