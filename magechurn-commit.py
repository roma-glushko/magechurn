import re
import pandas as pd
from pydriller import RepositoryMining, ModificationType
from domain.TestDetector import TestDetector
from domain.ModuleDetector import ModuleDetector

moduleMetrics = {}

#
# Collects statistic from git commits between releases
# Doesn't seem to be useful for churn analysis
# Will be replaced by magechurn.py
#

#for commit in RepositoryMining('../magento2-git', from_tag="2.3.4", to_tag="2.3.5-p1").traverse_commits():
for commit in RepositoryMining('../magento2-git', only_commits=['42d2163e2d0afa261411ae174b6fca23fe189045']).traverse_commits():
    print(commit.hash)

    for modification in commit.modifications:
        filePath = modification.old_path

        if modification.change_type == ModificationType.ADD:
            filePath = modification.new_path

        if TestDetector.isTestComponent(filePath):
            continue

        print(filePath)

        moduleName = ModuleDetector.getModule(filePath)

        print(moduleName)

        # collect statistic
        if moduleName not in moduleMetrics:
            moduleMetrics[moduleName] = {
                "files": {},
                "churnCount": 0,
            }

        if filePath not in moduleMetrics[moduleName]['files']:
            moduleMetrics[moduleName]['files'][filePath] = {
                "totalLoc": 0,
                "churnedLoc": 0,
                "deletedLoc": 0,
                "workedLoc": 0,
                "churnCount": 0,
                "status": "exist",
                "commits": "",
            }

        status = "exist"
        if modification.change_type == ModificationType.DELETE:
            status = "deleted"

        if modification.change_type == ModificationType.RENAME:
            oldFilePath = filePath
            filePath = modification.new_path
            # clean up duplicated record
            moduleMetrics[moduleName]['files'][filePath] = moduleMetrics[moduleName]['files'][oldFilePath]
            del moduleMetrics[moduleName]['files'][oldFilePath]

        moduleMetrics[moduleName]["churnCount"] += 1

        if modification.language_supported:
            moduleMetrics[moduleName]['files'][filePath]["totalLoc"] = modification.nloc
        else:
            if modification.source_code:
                moduleMetrics[moduleName]['files'][filePath]["totalLoc"] = sum([1 for i in modification.source_code.splitlines() if i.strip()])
            else:
                moduleMetrics[moduleName]['files'][filePath]["totalLoc"] = None

        moduleMetrics[moduleName]['files'][filePath]["status"] = status
        moduleMetrics[moduleName]['files'][filePath]["churnedLoc"] += modification.added
        moduleMetrics[moduleName]['files'][filePath]["deletedLoc"] += modification.removed
        moduleMetrics[moduleName]['files'][filePath]["workedLoc"] += modification.added + modification.removed
        moduleMetrics[moduleName]['files'][filePath]["churnCount"] += 1
        moduleMetrics[moduleName]['files'][filePath]["commits"] += " " + commit.hash

# save collected statistic

df = pd.DataFrame(columns=["module", "filePath", "status", "totalLoc", "churnedLoc", "deletedLoc", "workedLoc", "churnCount"])

for moduleName, moduleChurn in moduleMetrics.items():
    for filePath, fileChurn in moduleChurn['files'].items():
        df = df.append({
            "module": moduleName,
            "filePath": filePath,
            "status": fileChurn["status"],
            "totalLoc": fileChurn["totalLoc"],
            "churnedLoc": fileChurn["churnedLoc"],
            "deletedLoc": fileChurn["deletedLoc"],
            "workedLoc": fileChurn["workedLoc"],
            "churnCount": fileChurn["churnCount"],
            "commits": fileChurn["commits"],
        }, ignore_index=True)

df.to_csv(r'2.3.4-2.3.5-churn-statistic.csv', index = False, header=True)