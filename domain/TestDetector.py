
class TestDetector:

    @staticmethod
    def isTestComponent(file_path: str) -> bool:
        if file_path.startswith("dev/tests"):
            return True

        if "/Test/Unit/" in file_path:
            return True

        if "/Fixtures/" in file_path:
            return True

        if "/Test/Mftf/" in file_path:
            return True

        if "/Test/Integration/" in file_path:
            return True

        return False
