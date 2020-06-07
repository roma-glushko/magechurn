import os
from pydriller import GitRepository

#
# Collects statistic about module file count.
# Will be replaced by SourceAnalyzer.py
#

repository = GitRepository('../magento2-git')
repository._conf.set_value("main_branch", '2.4-develop')
commit235p1 = repository.get_commit_from_tag('2.3.5-p1')

repository.checkout(commit235p1.hash)

path, dirs, files = next(os.walk("../magento2-git/app/code/Magento/Cron"))
file_count = len(files)

print(file_count)