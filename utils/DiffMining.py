import logging
from pydriller import Modification, ModificationType
from pydriller.utils.conf import Conf
from git import Diff, Commit as GitCommit, NULL_TREE
from typing import List, Union

logger = logging.getLogger(__name__)


class DiffMining:
    def __init__(self, path_to_repo: Union[str, List[str]], commitA: GitCommit, commitB: GitCommit, conf=None):
        self.commitA = commitA
        self.commitB = commitB

        if conf is None:
            conf = Conf({
                "git_repo": None,
                "path_to_repo": path_to_repo,
            })

        self._conf = conf
        self._modifications = None

    @property
    def modifications(self) -> List[Modification]:
        if self._modifications is None:
            self._modifications = self._get_modifications()

        assert self._modifications is not None
        return self._modifications

    def _get_modifications(self):
        options = {}
        if self._conf.get('histogram'):
            options['histogram'] = True

        if self._conf.get('skip_whitespaces'):
            options['w'] = True

        diff_index = self.commitA.diff(self.commitB,
                                       create_patch=True,
                                       **options)

        return self._parse_diff(diff_index)

    def _parse_diff(self, diff_index) -> List[Modification]:
        modifications_list = []
        for diff in diff_index:
            old_path = diff.a_path
            new_path = diff.b_path
            change_type = self._from_change_to_modification_type(diff)

            diff_and_sc = {
                'diff': self._get_decoded_str(diff.diff),
                'source_code_before': self._get_decoded_sc_str(
                    diff.a_blob),
                'source_code': self._get_decoded_sc_str(
                    diff.b_blob)
            }

            modifications_list.append(Modification(old_path, new_path,
                                                   change_type, diff_and_sc))

        return modifications_list

    def _get_decoded_str(self, diff):
        try:
            return diff.decode('utf-8', 'ignore')
        except (UnicodeDecodeError, AttributeError, ValueError):
            logger.debug('Could not load the diff of a '
                         'file in diff')
            return None

    def _get_decoded_sc_str(self, diff):
        try:
            return diff.data_stream.read().decode('utf-8', 'ignore')
        except (UnicodeDecodeError, AttributeError, ValueError):
            logger.debug('Could not load source code of a '
                         'file in commit')
            return None

    @staticmethod
    def _from_change_to_modification_type(diff: Diff):
        if diff.new_file:
            return ModificationType.ADD
        if diff.deleted_file:
            return ModificationType.DELETE
        if diff.renamed_file:
            return ModificationType.RENAME
        if diff.a_blob and diff.b_blob and diff.a_blob != diff.b_blob:
            return ModificationType.MODIFY

        return ModificationType.UNKNOWN
