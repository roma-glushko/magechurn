import re


class ModuleDetector:

    @staticmethod
    def getModule(file_path: str) -> str:
        moduleName = 'n/a'

        if file_path.startswith("lib/web"):
            return "lib/web"

        if file_path.startswith("setup/"):
            return "setup"

        if "Magento" in file_path:
            # detect magento module
            modulePattern = r"(.*)\/(Magento\/(\w+))\/"

            matches = re.findall(modulePattern, file_path)
            return matches[0][1]

        return moduleName