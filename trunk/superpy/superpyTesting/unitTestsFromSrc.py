"""Module to read in all the doctests from src that we want to test.

This module is designed so that "python setup.py test" can just look in
here and automatically suck in the other doctests from the source.
"""

import unittest, doctest
import superpy
from superpy.core import Process, DataStructures

def MakeMainSuperpyDoctest():
    """Return a unittest.TestSuite object representing doctests from source code
    """
    suite = unittest.TestSuite()
    testCase = doctest.DocTestSuite(superpy)
    suite.addTest(testCase)
    testCase = doctest.DocTestSuite(Process)
    suite.addTest(testCase)
    testCase = doctest.DocTestSuite(DataStructures)
    suite.addTest(testCase)

    return suite

mainTestSuite = MakeMainSuperpyDoctest()
