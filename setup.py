from setuptools import setup, find_packages

with open("requirements.txt") as f: # Open requirements file
    requirements = f.read().splitlines() # Read requirements from file

setup(
    name = "Game-Recommendation-System",
    version="0.1",
    author= "Nikunjkumar",
    packages= find_packages(), # Automatically find packages in the src directory
    install_requires = requirements, # Install dependencies from requirements file
)