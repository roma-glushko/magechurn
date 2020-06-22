from pygount.analysis import SourceAnalysis
from utils.SourceScanner import SourceScanner
from domain.TestDetector import TestDetector


class SourceAnalyzer:

    @staticmethod
    def analyze(module_path: str) -> dict:
        languageMap = {
            "JavaScript+Genshi Text": "JavaScript",
            "HTML+PHP": "PHTML",
        }

        source_scanner = SourceScanner([module_path + "**/*.*"])
        source_paths_and_groups_to_analyze = list(source_scanner.source_paths())

        sourceAnalysis = {}

        for source_path, group in source_paths_and_groups_to_analyze:
            if TestDetector.isTestComponent(source_path):
                continue

            statistics = SourceAnalysis.from_file(
                source_path,
                group,
            )

            lang = statistics.language

            # group languages
            if lang in languageMap:
                lang = languageMap[lang]

            if source_path.endswith("graphqls"):
                lang = "GraphQl"

            if lang not in sourceAnalysis:
                sourceAnalysis[lang] = {
                    "files": 0,
                    "nloc": 0,
                }

            # print(statistics.path)

            sourceAnalysis[lang]["files"] += 1
            sourceAnalysis[lang]["nloc"] += statistics.code_count

        return sourceAnalysis
