"""
PaStA - Patch Stack Analysis

Copyright (c) OTH Regensburg, 2019-2021

Author:
  Ralf Ramsauer <ralf.ramsauer@oth-regensburg.de>

This work is licensed under the terms of the GNU GPL, version 2.  See
the COPYING file in the top-level directory.
"""

import re

from logging import getLogger
from multiprocessing import Pool, cpu_count

from .MAINTAINERS import load_maintainers
from .MailCharacteristics import MailCharacteristics, PatchType, email_get_header_normalised, email_get_from
from .Util import mail_parse_date, load_pkl_and_update

log = getLogger(__name__[-15:])

_repo = None
_maintainers_version = None
_clustering = None

MAIL_STRIP_TLD_REGEX = re.compile(r'(.*)\..+')


def ignore_tld(address):
    match = MAIL_STRIP_TLD_REGEX.match(address)
    if match:
        return match.group(1)

    return address


def ignore_tlds(addresses):
    return {ignore_tld(address) for address in addresses if address}


class LinuxMailCharacteristics (MailCharacteristics):
    BOTS = {'tip-bot2@linutronix.de', 'tipbot@zytor.com',
            'noreply@ciplatform.org', 'patchwork@emeril.freedesktop.org'}
    POTENTIAL_BOTS = {'broonie@kernel.org', 'lkp@intel.com'}

    REGEX_COMMIT_UPSTREAM = re.compile('.*commit\s+.+\s+upstream.*', re.DOTALL | re.IGNORECASE)
    REGEX_GREG_ADDED = re.compile('patch \".*\" added to .*')
    ROOT_FILES = ['.clang-format',
                  '.cocciconfig',
                  '.get_maintainer.ignore',
                  '.gitignore',
                  '.gitattributes',
                  '.mailmap',
                  'COPYING',
                  'CREDITS',
                  'Kbuild',
                  'Kconfig',
                  'README',
                  'MAINTAINERS',
                  'Makefile']
    ROOT_DIRS = ['Documentation/',
                 'LICENSES/',
                 'arch/',
                 'block/',
                 'certs/',
                 'crypto/',
                 'drivers/',
                 'fs/',
                 'include/',
                 'init/',
                 'ipc/',
                 'kernel/',
                 'lib/',
                 'mm/',
                 'net/',
                 'samples/',
                 'scripts/',
                 'security/',
                 'sound/',
                 'tools/',
                 'usr/',
                 'virt/',
                 # not yet merged subsystems
                 'kunit/']

    PROCESSES = ['linux-next', 'git pull', 'rfc']

    def _is_from_bot(self):
        email = self.mail_from[1].lower()
        subject = email_get_header_normalised(self.message, 'subject')
        uagent = email_get_header_normalised(self.message, 'user-agent')
        xmailer = email_get_header_normalised(self.message, 'x-mailer')
        x_pw_hint = email_get_header_normalised(self.message, 'x-patchwork-hint')
        potential_bot = email in LinuxMailCharacteristics.POTENTIAL_BOTS

        if email in LinuxMailCharacteristics.BOTS:
            return True

        if potential_bot:
            if x_pw_hint == 'ignore':
                return True

            # Mark Brown's bot and lkp
            if subject.startswith('applied'):
                return True

        if LinuxMailCharacteristics.REGEX_GREG_ADDED.match(subject):
            return True

        # AKPM's bot. AKPM uses s-nail for automated mails, and sylpheed for
        # all other mails. That's how we can easily separate automated mails
        # from real mails. Secondly, akpm acts as bot if the subject contains [merged]
        if email == 'akpm@linux-foundation.org':
            if 's-nail' in uagent or '[merged]' in subject:
                return True
            if 'mm-commits@vger.kernel.org' in self.lists:
                return True

        # syzbot - email format: syzbot-hash@syzkaller.appspotmail.com
        if 'syzbot' in email and 'syzkaller.appspotmail.com' in email:
            return True

        if xmailer == 'tip-git-log-daemon':
            return True

        # Stephen Rothwell's automated emails (TBD: generates false positives)
        if self.is_next and 'sfr@canb.auug.org.au' in email:
            return True

        return False

    def _is_stable_review(self):
        if 'X-Mailer' in self.message and \
           'LinuxStableQueue' in self.message['X-Mailer']:
            return True

        if 'X-stable' in self.message:
            xstable = self.message['X-stable'].lower()
            if xstable == 'commit' or xstable == 'review':
                return True

        # The patch needs to be sent to the stable list
        if not ('stable' in self.lists or
                'stable@vger.kernel.org' in self.recipients_lists):
            return False

        message_flattened = '\n'.join(self.patch.message).lower()

        if 'review patch' in message_flattened:
            return True

        if 'upstream commit' in message_flattened:
            return True

        # Greg uses this if the patch doesn't apply to a stable tree
        if 'the patch below does not apply to the' in message_flattened:
            return True

        if LinuxMailCharacteristics.REGEX_COMMIT_UPSTREAM.match(message_flattened):
            return True

        return False

    def _is_next(self):
        if 'linux-next' in self.lists:
            return True

        if 'linux-next@vger.kernel.org' in self.recipients_lists:
            return True

        return False

    def list_matches_patch(self, list):
        for lists, _, _ in self.maintainers.values():
            if list in lists:
                return True
        return False

    def __init__(self, repo, maintainers_version, clustering, message_id):
        super().__init__(repo, clustering, message_id)
        self.__init(repo, maintainers_version, clustering)
        self._cleanup()


    def __init(self, repo, maintainers_version, clustering):
        self.is_stable_review = False

        # stuff for maintainers analysis
        self.maintainers = dict()

        self.is_next = self._is_next()
        self.is_from_bot = self._is_from_bot()

        # Messages can be received by bots, or linux-next, even if they
        # don't contain patches
        if self.is_from_bot:
            self.type = PatchType.BOT
        elif self.is_next:
            self.type = PatchType.NEXT

        if not self.is_patch:
            return

        self.is_stable_review = self._is_stable_review()
        if self.is_stable_review:
            self.type = PatchType.STABLE

        # Exit, if we don't patch Linux
        if not self.patches_project:
            return

        # Now we can say it's a regular patch, if we still have the type 'other'
        if self.type == PatchType.OTHER:
            self.type = PatchType.PATCH

        if maintainers_version is None:
            return

        maintainers = maintainers_version[self.version]
        sections = maintainers.get_sections_by_files(self.patch.diff.affected)
        for section in sections:
            s_lists, s_maintainers, s_reviewers = maintainers.get_maintainers(section)
            s_maintainers = {x[1] for x in s_maintainers if x[1]}
            s_reviewers = {x[1] for x in s_reviewers if x[1]}
            self.maintainers[section] = s_lists, s_maintainers, s_reviewers

        if not self.first_upstream:
            return

        # In case the patch was integrated, fill the fields committer
        # and integrated_by_maintainer. integrated_by_maintainer indicates
        # if the patch was integrated by a maintainer that is responsible
        # for a section that is affected by the patch. IOW: The field
        # indicates if the patch was picked by the "correct" maintainer
        upstream = repo[self.first_upstream]
        self.committer = upstream.committer.name.lower()
        self.integrated_by_maintainer = False
        for section in maintainers.get_sections_by_files(upstream.diff.affected):
            _, s_maintainers, _ = maintainers.get_maintainers(section)
            if self.committer in [name for name, mail in s_maintainers]:
                self.integrated_by_maintainer = True
                break


def _load_mail_characteristic(message_id):
    return message_id, LinuxMailCharacteristics(_repo, _maintainers_version,
                                                _clustering, message_id)


def load_linux_mail_characteristics(config, clustering,
                                    ids):
    repo = config.repo

    tags = {repo.patch_get_version(repo[x]) for x in clustering.get_downstream()}
    maintainers_version = load_maintainers(config, tags)

    def _load_characteristics(ret):
        if ret is None:
            ret = dict()

        missing = ids - ret.keys()
        if len(missing) == 0:
            return ret, False

        global _repo, _maintainers_version, _clustering
        _maintainers_version = maintainers_version
        _clustering = clustering
        _repo = repo
        p = Pool(processes=int(0.25*cpu_count()), maxtasksperchild=4)

        missing = p.map(_load_mail_characteristic, missing, chunksize=1000)
        missing = dict(missing)
        print('Done')
        p.close()
        p.join()
        _repo = None
        _maintainers_version = None
        _clustering = None

        return {**ret, **missing}, True

    log.info('Loading/Updating Linux patch characteristics...')
    characteristics = load_pkl_and_update(config.f_characteristics_pkl,
                                          _load_characteristics)

    return characteristics
