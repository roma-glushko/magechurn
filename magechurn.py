import pandas as pd
import json
from git import Repo
from pydriller import ModificationType, RepositoryMining
from utils.DiffMining import DiffMining
from domain.TestDetector import TestDetector
from domain.ModuleDetector import ModuleDetector
from domain.ModulePathResolver import ModulePathResolver
from analysis.SourceAnalyzer import SourceAnalyzer

#
# Collects statistic from git commits and diffs between releases
#

repo = Repo("../magento2-git")

releaseA = repo.commit("2.3.4")
releaseB = repo.commit("2.3.5-p1")

# we need to count files in the new release for each module
repo.git.checkout(releaseB)

changelogMetrics = {}

# collects main statistics

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
    if moduleName not in changelogMetrics:

        modulePath = ModulePathResolver.getModulePath(filePath)

        moduleSourceStats = {}
        if moduleName != "n/a":
            moduleSourceStats = SourceAnalyzer.analyze("../magento2-git/" + modulePath)

        changelogMetrics[moduleName] = {
            "path": modulePath,
            "sourceStats": moduleSourceStats,
            "totalLoc": 0,
            "churnedLoc": 0,
            "deletedLoc": 0,
            "workedLoc": 0,
            "files": {},
            "authors": [],
            "commits": [],
        }

    if filePath not in changelogMetrics[moduleName]['files']:
        changelogMetrics[moduleName]['files'][filePath] = {
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
        changelogMetrics[moduleName]['files'][filePath] = changelogMetrics[moduleName]['files'][oldFilePath]
        del changelogMetrics[moduleName]['files'][oldFilePath]

    if modification.language_supported:
        changelogMetrics[moduleName]['files'][filePath]["totalLoc"] = modification.nloc
    else:
        if modification.source_code:
            changelogMetrics[moduleName]['files'][filePath]["totalLoc"] = sum(
                [1 for i in modification.source_code.splitlines() if i.strip()])
        else:
            changelogMetrics[moduleName]['files'][filePath]["totalLoc"] = None

    changelogMetrics[moduleName]['files'][filePath]["status"] = status
    changelogMetrics[moduleName]['files'][filePath]["churnedLoc"] += modification.added
    changelogMetrics[moduleName]['files'][filePath]["deletedLoc"] += modification.removed
    changelogMetrics[moduleName]['files'][filePath]["workedLoc"] += modification.added + modification.removed

    changelogMetrics[moduleName]["churnedLoc"] += modification.added
    changelogMetrics[moduleName]["deletedLoc"] += modification.removed
    changelogMetrics[moduleName]["workedLoc"] += modification.added + modification.removed

# collects commit statistics

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

        if moduleName not in changelogMetrics:
            continue

        if filePath not in changelogMetrics[moduleName]["files"]:
            continue

        changelogMetrics[moduleName]["files"][filePath]["commits"].append(commit.hash)
        changelogMetrics[moduleName]["files"][filePath]["authors"].append(commit.author.email)

        changelogMetrics[moduleName]["commits"].append(commit.hash)
        changelogMetrics[moduleName]["authors"].append(commit.author.email)

# save collected statistics
## by changelog/files

fileDataframe = pd.DataFrame(
    columns=["module", "filePath", "status", "totalLoc", "churnedLoc", "deletedLoc", "workedLoc", "commits", "authors"]
)

for moduleName, moduleChurn in changelogMetrics.items():
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

fileDataframe.to_csv(r'tmp/2.3.4-2.3.5.diff.churn.files.csv', index=False, header=True)

# aggregated module churn stats
## by changelog/files

moduleDataframe = pd.DataFrame(
    columns=["module", "path", "fileCount", "churnedLoc", "deletedLoc", "workedLoc", "commitCount", "authorCount"]
)

for moduleName, moduleChurn in changelogMetrics.items():
    moduleDataframe = moduleDataframe.append({
        "module": moduleName,
        "path": moduleChurn["path"],
        "sourceStats": json.dumps(moduleChurn["sourceStats"], sort_keys=True),
        "churnedLoc": moduleChurn["churnedLoc"],
        "deletedLoc": moduleChurn["deletedLoc"],
        "workedLoc": moduleChurn["workedLoc"],
        "commitCount": len(moduleChurn["commits"]),
        "authorCount": len(moduleChurn["authors"]),
    }, ignore_index=True)

moduleDataframe.to_csv(r'tmp/2.3.4-2.3.5.diff.churn.modules.csv', index=False, header=True)