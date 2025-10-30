import os
os.environ['KIVY_NO_CONSOLELOG'] = '1'
os.environ['KIVY_NO_ARGS'] = '1'
os.environ['KIVY_NO_FILELOG'] = '1'

import unittest
import sys

if __name__ == '__main__':
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromName('test_route_card_app')
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    sys.exit(0 if result.wasSuccessful() else 1)
