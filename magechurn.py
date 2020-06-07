import pandas as pd
from git import Repo
from pydriller import ModificationType, RepositoryMining
from utils.DiffMining import DiffMining
from domain.TestDetector import TestDetector
from domain.ModuleDetector import ModuleDetector

#
# Collects statistic from git commits and diffs between releases
#

repo = Repo("../magento2-git")

releaseA = repo.commit("2.3.4")
releaseB = repo.commit("2.3.5-p1")

moduleMetrics = {}

for modification in DiffMining("../magento2-git", releaseA, releaseB).modifications:
    filePath = modification.old_path

    if modification.change_type == ModificationType.ADD:
        filePath = modification.new_path

    print(filePath)

    if TestDetector.isTestComponent(filePath):
        continue

    moduleName = ModuleDetector.getModule(filePath)

    print(moduleName)

    # collect statistic
    if moduleName not in moduleMetrics:
        moduleMetrics[moduleName] = {
            "path": "",
            "totalLoc": {},
            "fileCount": 0,
            "files": {},
            "authors": [],
            "commits": [],
        }



    if filePath not in moduleMetrics[moduleName]['files']:
        moduleMetrics[moduleName]['files'][filePath] = {
            "totalLoc": 0,
            "churnedLoc": 0,
            "deletedLoc": 0,
            "workedLoc": 0,
            "status": "exist",
            "authors": [],
            "commits": [],
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

    if modification.language_supported:
        moduleMetrics[moduleName]['files'][filePath]["totalLoc"] = modification.nloc
    else:
        if modification.source_code:
            moduleMetrics[moduleName]['files'][filePath]["totalLoc"] = sum(
                [1 for i in modification.source_code.splitlines() if i.strip()])
        else:
            moduleMetrics[moduleName]['files'][filePath]["totalLoc"] = None

    moduleMetrics[moduleName]['files'][filePath]["status"] = status
    moduleMetrics[moduleName]['files'][filePath]["churnedLoc"] += modification.added
    moduleMetrics[moduleName]['files'][filePath]["deletedLoc"] += modification.removed
    moduleMetrics[moduleName]['files'][filePath]["workedLoc"] += modification.added + modification.removed

for commit in RepositoryMining('../magento2-git', from_commit=releaseA.hexsha, to_commit=releaseB.hexsha).traverse_commits():
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

        if moduleName not in moduleMetrics:
            continue

        if filePath not in moduleMetrics[moduleName]['files']:
            continue

        moduleMetrics[moduleName]['files'][filePath]["commits"].append(commit.hash)
        moduleMetrics[moduleName]['files'][filePath]["authors"].append(commit.author.email)

        moduleMetrics[moduleName]["commits"].append(commit.hash)
        moduleMetrics[moduleName]["authors"].append(commit.author.email)

# save collected statistic

fileDataframe = pd.DataFrame(
    columns=["module", "filePath", "status", "totalLoc", "churnedLoc", "deletedLoc", "workedLoc", "commits", "authors"]
)

for moduleName, moduleChurn in moduleMetrics.items():
    for filePath, fileChurn in moduleChurn['files'].items():
        fileDataframe = fileDataframe.append({
            "module": moduleName,
            "filePath": filePath,
            "status": fileChurn["status"],
            "totalLoc": fileChurn["totalLoc"],
            "churnedLoc": fileChurn["churnedLoc"],
            "deletedLoc": fileChurn["deletedLoc"],
            "workedLoc": fileChurn["workedLoc"],
            "commits": " ".join(fileChurn["commits"]),
            "authors": " ".join(fileChurn["authors"]),
        }, ignore_index=True)

fileDataframe.to_csv(r'2.3.4-2.3.5.diff.churn.files.csv', index=False, header=True)