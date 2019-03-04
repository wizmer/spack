from setuptools import setup

setup(
    name='Spack Deploy',
    version='0.2',
    py_modules=['spackd', 'modcheck'],
    install_requires=[
        'Click',
        'PyYAML'
    ],
    entry_points={
        'console_scripts': [
            'spackd = spackd:spackd',
            'modcheck = modcheck:run'
        ]
    }
)
