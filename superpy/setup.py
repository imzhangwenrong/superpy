"""Setup script for installing/distribuging package.
"""


from setuptools import setup, find_packages
setup(
    name = "superpy",
    version = "1.0",
    packages = find_packages(),
    scripts = ['superpy/scripts/%s' %s for s in [
    'CleanOldTasks.py', 'ShowServer.py', 'Spawn.py', 'SpawnAsService.py',
    'StartSuperWatch.py']],
    # metadata for upload to PyPI
    author = "Emin Martinian, Li Lee, Henry Xu",
    author_email = "emin.martinian@gmail.com",
    description = "Parallel processing tools for supercomputing with python.",
    license = "MIT",
    keywords = "parallel, super, process",
    requires = ['Pmw'],
    provides = ['superpy'],
    url = "http://code.google.com/p/superpy/",   # project home page
    
    # could also include long_description, download_url, classifiers, etc.
)
