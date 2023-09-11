from setuptools import setup

setup(
    name="teco",
    version="0.2.0",
    description="TECO - LCA calculation extension for TEASER and TEASERplus",
    url="https://github.com/RWTH-EBC/TEASER",
    author="RWTH Aachen University, E3D, "
    "Institute of Energy Efficiency and Sustainable Building",
    author_email="e3dr@e3d.rwth-aachen.de",
    license="MIT",
    packages=[
        "teco",
        "teco.logic",
        "teco.logic.buildingobjects",
        "teco.logic.buildingobjects.buildingphysics",
        "teco.data",
        "teco.data.input",
        "teco.data.input.inputdata",
        "teco.data.output",
    ],
    package_data={
        "teco.data.input.inputdata": ["*.json"]
    },
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Intended Audience :: Science/Research",
        "Topic :: Software Development :: Code Generators",
        "Topic :: Scientific/Engineering",
        "Topic :: Utilities",
    ],
    install_requires=["teaserplus"],
)

