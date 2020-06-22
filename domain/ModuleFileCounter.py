import re
import os.path
from domain.TestDetector import TestDetector


class ModuleFileCounter:

    @staticmethod
    def countFiles(module_path: str) -> int:
        count = 0

        for rootPath, dirs, files in os.walk(module_path):
            for fileName in files:
                full_path = os.path.join(rootPath, fileName)

                if os.path.isfile(full_path) and not TestDetector.isTestComponent(full_path) and full_path.endswith(('php', 'phtml', 'js', 'html')):
                    count += 1

        return count