import os, sys
app_root = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, app_root)
import __init__
from __init__ import app as application

import sys
sys.stdout = sys.stderr
