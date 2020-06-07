import os
import glob
import logging
from pygount.analysis import SourceScanner

_log = logging.getLogger("pygount")


class SourceScanner(SourceScanner):
    def _paths_and_group_to_analyze(self, path_to_analyse_pattern, group=None):
        for path_to_analyse in glob.glob(path_to_analyse_pattern, recursive=True):
            if os.path.islink(path_to_analyse):
                _log.debug("skip link: %s", path_to_analyse)
            else:
                is_folder = os.path.isdir(path_to_analyse)
                if self._is_path_to_skip(os.path.basename(path_to_analyse), is_folder):
                    _log.debug("skip due to matching skip pattern: %s", path_to_analyse)
                else:
                    actual_group = group
                    if is_folder:
                        if actual_group is None:
                            actual_group = os.path.basename(path_to_analyse)
                            if actual_group == "":
                                # Compensate for trailing path separator.
                                actual_group = os.path.basename(os.path.dirname(path_to_analyse))
                        yield from self._paths_and_group_to_analyze_in(path_to_analyse_pattern, actual_group)
                    else:
                        if actual_group is None:
                            actual_group = os.path.dirname(path_to_analyse)
                            if actual_group == "":
                                actual_group = os.path.basename(os.path.dirname(os.path.abspath(path_to_analyse)))
                        yield path_to_analyse, actual_group