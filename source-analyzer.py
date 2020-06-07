from pygount.analysis import DuplicatePool, SourceAnalysis
from utils.SourceScanner import SourceScanner

#
# Collects statistic from new release module states
#

source_scanner = SourceScanner(["../magento2-git/app/code/Magento/Catalog/**/*.*"], folders_to_skip=[r'((.*)\/Test\/(.*))'])

source_paths_and_groups_to_analyze = list(source_scanner.source_paths())
duplicate_pool = DuplicatePool()

for source_path, group in source_paths_and_groups_to_analyze:
    statistics = SourceAnalysis.from_file(
        source_path,
        group,
    )

    print(statistics.path)
    print(statistics.language)
    print(statistics.code_count)
