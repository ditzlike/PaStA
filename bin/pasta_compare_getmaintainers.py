import tempfile
import shutil
from pypasta import LinuxMailCharacteristics
from pypasta.LinuxMaintainers import load_maintainers, LinuxSubsystem
import subprocess
import os
import random
import argparse
import re
from logging import getLogger
from collections import defaultdict

log = getLogger(__name__[-15:])
#from RalfScriptLauncher.PaStA.pypasta.LinuxMailCharacteristics import patch
#TODO: ignore all the pl warnings thrown
def compare_getmaintainers(config, prog, argv):

    def repo_get_and_write_file(ref, filename, destination, content=None):
        if content is None:
            content = repo.get_blob(ref, filename)
        with open(os.path.join(destination, filename), "wb") as f:
            f.write(content)

    parser = argparse.ArgumentParser(prog=prog, description='compare PaStA and official get_maintainer')
    # parser.add_argument('--mbox', metavar='mbox', type=str, nargs='+', help='Which mbox the message_id\'s'
    #                                                                      ' are supposed come from')
    parser.add_argument('--m_id', metavar='m_id', type=str, nargs='+', help="Which message_id\'s to use\n"
                                                                            "Important: see to it that the mailboxes"
                                                                            " affected by the provided id's are "
                                                                            "active in the current Config")

    args = parser.parse_args(argv)

    # mailboxes = args.mbox
    arg_ids = args.m_id

    linusTorvaldsTuple = (
        'torvalds@linux-foundation.org', str(LinuxSubsystem.Status.Buried), "THE REST")

    repo = config.repo
    repo.register_mbox(config)

    if arg_ids is None:
        test_list = list(repo.mbox.get_ids(allow_invalid=False))
        arg_ids = [random.choice(test_list)]

    message_dict = defaultdict(list)
    [message_dict[LinuxMailCharacteristics._patch_get_version_static(repo[x], repo)]
         .append(x) for x in arg_ids]

    # loads a dictionary with another dictionary of subsystems for each version
    # structure is 'vxx-rc5' <... object at ...>, etc
    maintainers_version = load_maintainers(config, message_dict.keys())

    # making a few directories to trick the script into thinking it is inside a linux repository

    fakeLinuxPath = tempfile.mkdtemp()

    try:

        fakeDirsNames = ["arch", "Documentation", "drivers", "fs", "include", "init", "ipc", "kernel", "lib", "scripts"]
        # create a directory for every string in fakeDirsNames
        for dir in fakeDirsNames:
            os.mkdir(os.path.join(fakeLinuxPath, dir))

        fakeFileNames = ["COPYING", "CREDITS", "Kbuild", "Makefile", "README"]
        # create a file for every fake file name needed for the script
        for file in fakeFileNames:
            open(os.path.join(fakeLinuxPath, file), 'a').close()

        for key_version in message_dict:

            # build the structure anew for every different version
            repo_get_and_write_file(key_version, "MAINTAINERS", fakeLinuxPath)
            repo_get_and_write_file(key_version, "scripts/get_maintainer.pl", fakeLinuxPath)

            for message_id in message_dict[key_version]:

                log.info("\n\nSTARTING COMPARISON FOR MESSAGE TUPLE: " + str(message_id))

                # repo[message_id] retrieves the patchmail object for that message id
                patch = repo[message_id]

                log.info('\nVersion of currently analyzed patch is ' + key_version)

                # taken from the last few lines of __init__ in LinuxMailCharacteristics
                linux_maintainers = maintainers_version[key_version]

                subsystems = linux_maintainers.get_subsystems_by_files(patch.diff.affected)

                # GETTING NORMALIZED PASTA MAINTAINERS START

                pasta_maintainers = list()
                for subsystem in subsystems:
                    lists, maintainers, reviewers = linux_maintainers.get_maintainers(subsystem)

                    for mail_list in lists:
                        '''from what I've seen these things are either 'moderated list' or
                        'open list', but no way of telling which
                        therefore I leave the status and the subsystem in these cases out entirely
                        explicitely no subsystem here although I could. Makes the comparison easier, since the pl data
                        doesn't have a subsystem defined in these lists here
                        '''
                        # trimming x to remove bothersome whitespaces disrupting the comparison
                        tuple = (mail_list.strip(), "", "")

                        if tuple not in pasta_maintainers:
                            # no subsystem needed for those cases
                            pasta_maintainers.append(tuple)

                    for maintainer in maintainers:
                        # appending it in the same structure the perl script generates
                        linuxSubsys_obj = linux_maintainers[subsystem]

                        if len(linuxSubsys_obj.status) != 1:
                            # Idk in which cases there are no or more than one status, so I made this thing here and just took the first element for now
                            log.error(
                                "IMPORTANT: had more than one status or none? Lookup maintain_tuple " + str(maintainer)
                                + " in retrieved " + str(maintainers))

                        # TODO: prolly unfinshed, lookup more examples later
                        # the Status enum doesn't precicely have the structure provided by get_maintainers.pl, must be minorly adjusted
                        status = linuxSubsys_obj.status[0]
                        if status is LinuxSubsystem.Status.Maintained:
                            status = "maintainer"

                        elif status is LinuxSubsystem.Status.Supported:
                            status = "supporter"

                        else:
                            status = str(status)

                        to_be_appended = (maintainer[1].strip(), status, subsystem)

                        if to_be_appended != linusTorvaldsTuple:
                            pasta_maintainers.append(to_be_appended)

                        # Doing nothing with the reviewers

                # /NORMALIZED PASTA MAINTAINERS END

                log.info("maintainers successfully retrieved by PaStA")

                tempMailPath = tempfile.mkdtemp()
                try:

                    message_raw = repo.mbox.get_raws(message_id)[0]
                    repo_get_and_write_file(None, "m", tempMailPath, content=message_raw)

                    os.chdir(fakeLinuxPath)

                    pl_output = subprocess.run(
                        ['perl ' + os.path.join(fakeLinuxPath, os.path.join("scripts", "get_maintainer.pl")) + ' '
                         + str(os.path.join(tempMailPath, "m"))
                         + ' --subsystem --status --separator \; --nogit --nogit-fallback --roles --norolestats']
                        , shell=True
                        , stdout=subprocess.PIPE).stdout.decode("utf-8")

                    if pl_output == "":
                        log.error("perl script did not deliver any sort of output, nothing to compare. Exiting")
                        return
                finally:
                    shutil.rmtree(tempMailPath)


        # NORMALIZE PL DATA
        '''
        aim of this part of code: bring the big string of get_maintainers.pl into the form of a list of tupels
        tupels being: mail; status; Subsystem
        status such as 'supported' or 'maintained'
        pl_output is in form of: (element), (element)\n...alive in reporters\n[subsystemlist]
        We don't care for the last two lines, we only consider the first line with comma separated values
        '''
        pl_csv = pl_output.split('\n')[0]
        pl_csv_elements = pl_csv.split(';')
        pl_maintainers = list()
        for pl_element in pl_csv_elements:
            '''
            pl_element has the following structure: name <mail> (status:subsystem)
            I want to extract the email, the status and the subsystem inside a tuple for later comparison
            '''
            # special case open and moderated list, where we don't consider the status or the subsystem
            if '(open list' in pl_element or 'moderated list' in pl_element:
                #get everything until the first (, but excluding it
                name = re.search("[^\(]*", pl_element).group(0)
                pl_maintainers.append((name.strip(), "", ""))
                continue
            #works on the assumption that the mail of the maintainer is between < and >
            #works with lookahead and lookbehind
            name = re.search("(?<=<)(.*?)(?=>)", pl_element).group(0)
            # works on the assumption that after the first ( and in between the first: there's the status
            status = re.search("(?<=\()(.*?)(?=:)", pl_element).group(0)
            # cut from after the first occurence of : till before the last occurrence of )
            subsystem = re.search("(?<=:)(.*)(?=\))", pl_element).group(0)
            pl_maintainers.append((name, status, subsystem))
        # /NORMALIZE PL DATA END
        log.info("Comparing pasta and pl output for message-id: " + message_id)
        # important: pasta_maintainers is being modified through this method. Cannot be used the same way afterwards
        # STARTING COMPARISON OF PL AND PASTA
        # nested helper method to check for the equality of a pl and a pasta tuple
        def equal_name_status(pl_tuple, pasta_tuple):
            is_equal = True
            if pl_tuple[1] != pasta_tuple[1]:
                log.error(
                    "\tEntry 1 (Status) didn't match\n\tSupposed to be: " + str(pl_tuple[1]) + ", but was " + str(
                        pasta_tuple[1]))
                is_equal = False
            '''the pl script abbreviates long subsystem names with '...' which disrupts the comparison
            in such cases, only look if the pl_tuple without the last 3 chars is a substring of pasta_tuple'''
            if pl_tuple[2][-3:] == '...':
                if pl_tuple[2][:-3] not in pasta_tuple[2]:
                    log.error("\tEntry 2 (Subsystem) didn't match"
                                "\n\tSupposed to be: " + str(pl_tuple[2]) + ", but was " + str(pasta_tuple[2]))
                    is_equal = False
            elif pl_tuple[2] != pasta_tuple[2]:
                is_equal = False
                log.error("\tEntry 2 (Subsystem) didn't match"
                            "\n\tSupposed to be: " + str(pl_tuple[2]) + ", but was " + str(pasta_tuple[2]))
            return is_equal
        log.info("Starting comparison of perl maintainers and pasta maintainers")
        # TODO: see if I can look for duplicate tupels in both lists, more importantly pasta_m and eliminate them?
        for pl_tuple in pl_maintainers:
            log.info("Comparing pl_tuple " + str(pl_tuple))
            pasta_tuple = next((x for x in pasta_maintainers if x[0].lower() == pl_tuple[0].lower()), None)
            if pasta_tuple is not None:
                # removing the element from the pasta_maintainers list, so I can later check for leftover elements
                del pasta_maintainers[pasta_maintainers.index(pasta_tuple)]
            else:
                # todo: build some data structures for missing/not found entries?
                log.error("!!! NO COMPARISON TUPLE FOR PL_TUPLE " + str(pl_tuple) + " FOUND !!!")
                continue
            if pl_tuple[1] == "" and pl_tuple[2] == "":
                log.info("\tPasta and pl script matched!")
                # no further comparson needed here because [0] already does match and the rest needn't match
                continue
            is_equal = equal_name_status(pl_tuple, pasta_tuple)
            if is_equal:
                log.info("\tPasta and pl script matched!")
            else:
                log.error("\tPasta and pl script did NOT match!")
        if len(pasta_maintainers) != 0:
            log.error(
                "Leftover elements in pasta_maintainers with not matching pl equal:\n" + str(pasta_maintainers))
        # END COMPARISON OF PL AND PAST

    finally:
        shutil.rmtree(fakeLinuxPath)

    # END COMPARISON OF PL AND PAST