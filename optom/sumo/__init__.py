import sys
import os
try:
    sys.path.append(os.path.join(os.path.dirname(
        "__file__"), '..', '..', '..', "tools"))  # tutorial in tests
    sys.path.append(os.path.join(os.environ.get("SUMO_HOME", os.path.join(
        os.path.dirname("__file__"), "..", "..")), "tools"))  # tutorial in docs
except ImportError:
    sys.exit("please declare environment variable 'SUMO_HOME' as the root" +
             "directory of your sumo installation (it should contain folders 'bin'," +
             "'tools' and 'docs')")
