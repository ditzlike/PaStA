"""
PaStA - Patch Stack Analysis

Copyright (c) OTH Regensburg, 2021

Author:
  Ralf Ramsauer <ralf.ramsauer@oth-regensburg.de>

This work is licensed under the terms of the GNU GPL, version 2.  See
the COPYING file in the top-level directory.
"""

from .MailCharacteristics import MailCharacteristics, PatchType


class QemuMailCharacteristics(MailCharacteristics):
    ROOT_DIRS = [
    ]
    ROOT_FILES = [
    ]

    # Additional lists that are not known by pasta
    LISTS = set()

    def __init__(self, repo, maintainers_version, clustering, message_id):
        super().__init__(repo, clustering, message_id)
        self.__init(repo, maintainers_version)
        self._cleanup()

    def __init(self, repo, maintainers_version):
        if self.is_from_bot:
            self.type = PatchType.BOT

        if not self.is_patch:
            return

        if self.type == PatchType.OTHER:
            self.type = PatchType.PATCH

        self._integrated_correct(repo, maintainers_version)
