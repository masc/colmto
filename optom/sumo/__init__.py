import sys
import os
try:
    sys.path.append(os.path.join("sumo", "sumo", "tools"))
    sys.path.append(os.path.join(os.environ.get("SUMO_HOME", os.path.join("..", "..")), "tools"))
except ImportError:
    sys.exit("please declare environment variable 'SUMO_HOME' as the root" +
             "directory of your sumo installation (it should contain folders 'bin'," +
             "'tools' and 'docs')")
