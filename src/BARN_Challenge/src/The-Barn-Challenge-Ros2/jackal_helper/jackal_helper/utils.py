import os
from os.path import dirname
from ament_index_python.packages import get_package_share_directory

def get_pkg_src_path(jackal_pkg = False):
    # Resolve directly via the installed share directory instead of guessing
    # the source tree layout — works regardless of workspace path/nesting.
    jackal_share_path = get_package_share_directory("jackal_helper")
    if jackal_pkg:
        return jackal_share_path
    return dirname(jackal_share_path)
