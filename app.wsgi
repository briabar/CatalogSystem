# enter our virtualenv
import os, sys
app_root = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, app_root)
print sys.path
del os, sys, app_root

# run the app
from main import main
