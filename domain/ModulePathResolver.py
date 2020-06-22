import re


class ModulePathResolver:

    @staticmethod
    def getModulePath(file_path: str) -> str:
        modulePath = '/'

        if file_path.startswith("lib/web"):
            return "lib/web"

        if file_path.startswith("setup/"):
            return "setup"

        if "Magento" in file_path:
            # detect Magento module path
            modulePathPattern = r"^((.*)\/(Magento\/(\w+))\/)"

            matches = re.findall(modulePathPattern, file_path)
            return matches[0][0]

        return modulePath