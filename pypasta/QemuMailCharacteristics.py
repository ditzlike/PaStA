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
    ROOT_DIRS = ['accel/',
                 'audio/',
                 'authz/',
                 'backends/',
                 'block/',
                 'bsd-user/',
                 'capstone/',
                 'chardev/',
                 'contrib/',
                 'crypto/',
                 'darwin-user/',
                 'default-configs/',
                 'disas/',
                 'docs/',
                 'dtc/',
                 'dump/',
                 'ebpf/',
                 'fpu/',
                 'fsdev/',
                 'gdb-xml/',
                 'hw/',
                 'include/',
                 'io/',
                 'ldscripts/',
                 'libcacard/',
                 'libdecnumber/',
                 'linux-headers/',
                 'linux-user/',
                 'meson/',
                 'migration/',
                 'monitor/',
                 'nbd/',
                 'net/',
                 'pc-bios/',
                 'pixman/',
                 'plugins/',
                 'po/',
                 'python/',
                 'qapi/',
                 'qga/',
                 'QMP/',
                 'qobject/',
                 'qom/',
                 'replay/',
                 'roms/',
                 'scripts/',
                 'scsi/',
                 'semihosting/',
                 'slirp/',
                 'softmmu/',
                 'storage-daemon/',
                 'stubs/',
                 'subprojects/',
                 'sysconfigs/',
                 'target/',
                 'target-alpha/',
                 'target-arm/',
                 'target-cris/',
                 'target-i386/',
                 'target-lm32/',
                 'target-m68k/',
                 'target-microblaze/',
                 'target-mips/',
                 'target-moxie/',
                 'target-openrisc/',
                 'target-ppc/',
                 'target-s390x/',
                 'target-sh4/',
                 'target-sparc/',
                 'target-tilegx/',
                 'target-tricore/',
                 'target-unicore32/',
                 'target-xtensa/',
                 'tcg/',
                 'tests/',
                 'tools/',
                 'trace/',
                 'ui/',
                 'util/',
    ]

    ROOT_FILES = ['accel.c',
                  'acl.c',
                  'acl.h',
                  'aes.c',
                  'aes.h',
                  'aio.c',
                  'aio-posix.c',
                  'aio-win32.c',
                  'alpha-dis.c',
                  'alpha.ld',
                  'a.out.h',
                  'arch_init.c',
                  'arch_init.h',
                  'arm-dis.c',
                  'arm.ld',
                  'arm-semi.c',
                  'async.c',
                  'atomic_template.h',
                  'balloon.c',
                  'balloon.h',
                  'bitmap.c',
                  'bitmap.h',
                  'bitops.c',
                  'bitops.h',
                  'block.c',
                  'blockdev.c',
                  'blockdev.h',
                  'blockdev-nbd.c',
                  'block.h',
                  'block_int.h',
                  'blockjob.c',
                  'blockjob.h',
                  'block-migration.c',
                  'block-migration.h',
                  'bootdevice.c',
                  'bswap.h',
                  'bt-host.c',
                  'bt-host.h',
                  'bt-vhci.c',
                  'buffered_file.c',
                  'buffered_file.h',
                  'cache-utils.c',
                  'cache-utils.h',
                  'Changelog',
                  'check-qdict.c',
                  'check-qfloat.c',
                  'check-qint.c',
                  'check-qjson.c',
                  'check-qlist.c',
                  'check-qstring.c',
                  'cmd.c',
                  'cmd.h',
                  'CODING_STYLE',
                  'CODING_STYLE.rst',
                  'compatfd.c',
                  'compatfd.h',
                  'compiler.h',
                  'config.h',
                  'configure',
                  'console.c',
                  'console.h',
                  'COPYING',
                  'COPYING.LIB',
                  'COPYING.PYTHON',
                  'coroutine-gthread.c',
                  'coroutine-sigaltstack.c',
                  'coroutine-ucontext.c',
                  'coroutine-win32.c',
                  'cpu-all.h',
                  'cpu.c',
                  'cpu-common.h',
                  'cpu-defs.h',
                  'cpu-exec.c',
                  'cpu-exec-common.c',
                  'cpus.c',
                  'cpus-common.c',
                  'cpus.h',
                  'cputlb.c',
                  'cputlb.h',
                  'cris-dis.c',
                  'cursor.c',
                  'cursor_hidden.xpm',
                  'cursor_left_ptr.xpm',
                  'cutils.c',
                  'def-helper.h',
                  'device-hotplug.c',
                  'device_tree.c',
                  'device_tree.h',
                  'disas.c',
                  'disas.h',
                  'dis-asm.h',
                  'dma.h',
                  'dma-helpers.c',
                  'dump.c',
                  'dump.h',
                  'dump-stub.c',
                  'dyngen-exec.h',
                  'elf.h',
                  'envlist.c',
                  'envlist.h',
                  'error.c',
                  'error.h',
                  'error_int.h',
                  'event_notifier.c',
                  'event_notifier.h',
                  'event_notifier-posix.c',
                  'event_notifier-win32.c',
                  'exec-all.h',
                  'exec.c',
                  'exec-memory.h',
                  'exec-obsolete.h',
                  'exec-vary.c',
                  'gdbstub.c',
                  'gdbstub.h',
                  'gen-icount.h',
                  'gitdm.config',
                  'HACKING',
                  'hax-stub.c',
                  'hmp.c',
                  'hmp-commands.hx',
                  'hmp-commands-info.hx',
                  'hmp.h',
                  'host-utils.c',
                  'host-utils.h',
                  'hpet.h',
                  'hppa-dis.c',
                  'hppa.ld',
                  'hwaddr.h',
                  'i386-dis.c',
                  'i386.ld',
                  'ia64-dis.c',
                  'ia64.ld',
                  'input.c',
                  'int128.h',
                  'iohandler.c',
                  'ioport.c',
                  'ioport.h',
                  'ioport-user.c',
                  'iorange.h',
                  'iothread.c',
                  'iov.c',
                  'iov.h',
                  'job.c',
                  'job-qmp.c',
                  'json-lexer.c',
                  'json-lexer.h',
                  'json-parser.c',
                  'json-parser.h',
                  'json-streamer.c',
                  'json-streamer.h',
                  'Kconfig',
                  'Kconfig.host',
                  'kvm-all.c',
                  'kvm.h',
                  'kvm-stub.c',
                  'libfdt_env.h',
                  'LICENSE',
                  'linux-aio.c',
                  'lm32-dis.c',
                  'm68k-dis.c',
                  'm68k.ld',
                  'm68k-semi.c',
                  'main-loop.c',
                  'main-loop.h',
                  'MAINTAINERS',
                  'Makefile',
                  'Makefile.dis',
                  'Makefile.hw',
                  'Makefile.objs',
                  'Makefile.target',
                  'Makefile.user',
                  'memory.c',
                  'memory.h',
                  'memory-internal.h',
                  'memory_ldst.c.inc',
                  'memory_ldst.inc.c',
                  'memory_mapping.c',
                  'memory_mapping.h',
                  'memory_mapping-stub.c',
                  'meson.build',
                  'meson_options.txt',
                  'microblaze-dis.c',
                  'migration.c',
                  'migration-exec.c',
                  'migration-fd.c',
                  'migration.h',
                  'migration-rdma.c',
                  'migration-tcp.c',
                  'migration-unix.c',
                  'mips-dis.c',
                  'mips.ld',
                  'module.c',
                  'module-common.c',
                  'module.h',
                  'monitor.c',
                  'monitor.h',
                  'nbd.c',
                  'nbd.h',
                  'net.c',
                  'net-checksum.c',
                  'net.h',
                  'notify.c',
                  'notify.h',
                  'numa.c',
                  'osdep.c',
                  'osdep.h',
                  'oslib-posix.c',
                  'oslib-win32.c',
                  'os-posix.c',
                  'os-win32.c',
                  'page_cache.c',
                  'page-vary.c',
                  'page-vary-common.c',
                  'path.c',
                  'pci-ids.txt',
                  'pflib.c',
                  'pflib.h',
                  'poison.h',
                  'posix-aio-compat.c',
                  'ppc64.ld',
                  'ppc-dis.c',
                  'ppc.ld',
                  'qapi-schema-guest.json',
                  'qapi-schema.json',
                  'qapi-schema-test.json',
                  'qbool.c',
                  'qbool.h',
                  'qdev-monitor.c',
                  'qdict.c',
                  'qdict.h',
                  'qdict-test-data.txt',
                  'qemu-aio.h',
                  'qemu-barrier.h',
                  'qemu-bridge-helper.c',
                  'qemu-char.c',
                  'qemu-char.h',
                  'qemu-common.h',
                  'qemu-config.c',
                  'qemu-config.h',
                  'qemu-coroutine.c',
                  'qemu-coroutine.h',
                  'qemu-coroutine-int.h',
                  'qemu-coroutine-io.c',
                  'qemu-coroutine-lock.c',
                  'qemu-coroutine-sleep.c',
                  'qemu-deprecated.texi',
                  'qemu-doc.texi',
                  'qemu-edid.c',
                  'qemu-error.c',
                  'qemu-error.h',
                  'qemu-file.c',
                  'qemu-file.h',
                  'qemu-file-stdio.c',
                  'qemu-file-unix.c',
                  'qemu-ga.c',
                  'qemu-ga.texi',
                  'qemu-img.c',
                  'qemu-img-cmds.hx',
                  'qemu-img.texi',
                  'qemu-io.c',
                  'qemu-io-cmds.c',
                  'qemu-keymap.c',
                  'qemu-lock.h',
                  'qemu-log.c',
                  'qemu-log.h',
                  'qemu-malloc.c',
                  'qemu-nbd.c',
                  'qemu-nbd.texi',
                  'qemu.nsi',
                  'qemu-objects.h',
                  'qemu-option.c',
                  'qemu-option.h',
                  'qemu-option-internal.h',
                  'qemu-options.h',
                  'qemu-options.hx',
                  'qemu-options-wrapper.h',
                  'qemu-option-trace.texi',
                  'qemu-os-posix.h',
                  'qemu-os-win32.h',
                  'qemu-pixman.c',
                  'qemu-pixman.h',
                  'qemu-progress.c',
                  'qemu-queue.h',
                  'qemu.sasl',
                  'qemu-seccomp.c',
                  'qemu-seccomp.h',
                  'qemu_socket.h',
                  'qemu-sockets.c',
                  'qemu-storage-daemon.c',
                  'qemu-tech.texi',
                  'qemu-thread.c',
                  'qemu-thread.h',
                  'qemu-thread-posix.c',
                  'qemu-thread-posix.h',
                  'qemu-thread-win32.c',
                  'qemu-thread-win32.h',
                  'qemu-timer.c',
                  'qemu-timer-common.c',
                  'qemu-timer.h',
                  'qemu-tls.h',
                  'qemu-tool.c',
                  'qemu-user.c',
                  'qemu-x509.h',
                  'qemu-xattr.h',
                  'qerror.c',
                  'qerror.h',
                  'qfloat.c',
                  'qfloat.h',
                  'qint.c',
                  'qint.h',
                  'qjson.c',
                  'qjson.h',
                  'qlist.c',
                  'qlist.h',
                  'qmp.c',
                  'qmp-commands.hx',
                  'qobject.h',
                  'qstring.c',
                  'qstring.h',
                  'qtest.c',
                  'qtest.h',
                  'range.h',
                  'readline.c',
                  'readline.h',
                  'README',
                  'README.rst',
                  'replication.c',
                  'replication.h',
                  'rules.mak',
                  'rwhandler.c',
                  'rwhandler.h',
                  's390-dis.c',
                  's390.ld',
                  'savevm.c',
                  'sh4-dis.c',
                  'simpletrace.c',
                  'simpletrace.h',
                  'softmmu_defs.h',
                  'softmmu_exec.h',
                  'softmmu_header.h',
                  'softmmu-semi.h',
                  'softmmu_template.h',
                  'sparc64.ld',
                  'sparc-dis.c',
                  'sparc.ld',
                  'spice-qemu-char.c',
                  'sysemu.h',
                  'targphys.h',
                  'tcg-runtime.c',
                  'tci.c',
                  'tci-dis.c',
                  'test-coroutine.c',
                  'test-qmp-commands.c',
                  'test-visitor.c',
                  'thread-pool.c',
                  'thread-pool.h',
                  'thunk.c',
                  'thunk.h',
                  'TODO',
                  'tpm.c',
                  'trace-events',
                  'translate-all.c',
                  'translate-all.h',
                  'translate-common.c',
                  'uboot_image.h',
                  'uri.c',
                  'uri.h',
                  'usb-bsd.c',
                  'usb-linux.c',
                  'usb-redir.c',
                  'usb-stub.c',
                  'user-exec.c',
                  'user-exec-stub.c',
                  'VERSION',
                  'version.rc',
                  'vgafont.h',
                  'vl.c',
                  'vmstate.c',
                  'vmstate.h',
                  'win_dump.c',
                  'win_dump.h',
                  'x86_64.ld',
                  'xbzrle.c',
                  'xen-all.c',
                  'xen-common.c',
                  'xen-common-stub.c',
                  'xen-hvm.c',
                  'xen-hvm-stub.c',
                  'xen-mapcache.c',
                  'xen-mapcache.h',
                  'xen-stub.c',
                  'xtensa-semi.c',
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
