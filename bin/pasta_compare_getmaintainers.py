import tempfile

from pypasta import LinuxMailCharacteristics
from pypasta.LinuxMaintainers import load_maintainers, LinuxSubsystem
import subprocess
import os
import random
import argparse
from logging import getLogger
from collections import defaultdict

log = getLogger(__name__[-15:])
#from RalfScriptLauncher.PaStA.pypasta.LinuxMailCharacteristics import patch
#TODO: make the output more readable or find someplace to write it to, how to present data in general
#TODO: what to do with linus torvalds, buried, the rest? For now simply hardcoded ignored, deal with it later
#TODO: ignore all the pl warnings thrown
#TODO: searches for random message_id's in alsa devel hardcoded. Look for a more overall solution later
#TODO: random solution sometimes works - sometimes it doesn't. See to it that no broken/useless message_id's are chosen
def compare_getmaintainers(config, prog, argv):

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
        'linus torvalds <torvalds@linux-foundation.org>', str(LinuxSubsystem.Status.Buried), "THE REST")

    repo = config.repo
    repo.register_mbox(config)

    if arg_ids == None:
        # picking a random line of message_id's from mbox-result according to:
        # https://stackoverflow.com/questions/3540288/how-do-i-read-a-random-line-from-one-file-in-python
        with open(os.path.join("resources", "linux", "resources", "mbox", "index",
                               "pubin", "alsa-project.org", "alsa-devel", "0")) as f:
            randomLine = next(f)
            for num, aline in enumerate(f, 2):
                if random.randrange(num): continue
                randomLine = aline
        arg_ids = [randomLine.split(' ')[1]]  # there may be multiple message-ids in a row, so I split them by a space

    message_dict = defaultdict(list)
    [message_dict[LinuxMailCharacteristics._patch_get_version_static(repo[x], repo)]
         .append(x) for x in arg_ids]

    # loads a dictionary with another dictionary of subsystems for each version
    # structure is 'vxx-rc5' <... object at ...>, etc
    maintainers_version = load_maintainers(config, message_dict.keys())

    # making a few directories to trick the script into thinking it is inside a linux repository

    fakeLinuxPath = tempfile.mkdtemp()

    fakeDirsNames = ["arch", "Documentation", "drivers", "fs", "include", "init", "ipc", "kernel", "lib", "scripts"]
    # create a directory for every string in fakeDirsNames
    [os.mkdir(os.path.join(fakeLinuxPath, x)) for x in fakeDirsNames]

    fakeFileNames = ["COPYING", "CREDITS", "Kbuild", "Makefile", "README"]
    # create a file for every fake file name needed for the script
    [open(os.path.join(fakeLinuxPath, x), 'a').close for x in fakeFileNames]

    for key_version in message_dict:

        # the holy text of tempdir: https://www.programcreek.com/python/example/111/tempfile.mkdtemp

        # build the structure anew for every different version
        maintainers_file = repo.get_blob(key_version, "MAINTAINERS")
        maintainers_script = repo.get_blob(key_version, os.path.join("scripts", "get_maintainer.pl"))

        with open(os.path.join(fakeLinuxPath, "MAINTAINERS"), "wb+") as f:
            f.write(maintainers_file)

        with open(os.path.join(fakeLinuxPath, os.path.join("scripts", "get_maintainer.pl")), "wb") as f:
            f.write(maintainers_script)

        # TODO: no tuple no more
        for message_id in message_dict[key_version]:

            log.info("\n\nSTARTING COMPARISON FOR MESSAGE TUPLE: " + str(message_id))

            # repo[message_id] retrieves the patchmail object for that message id
            patch = repo[message_id]

            log.info('\nVersion of currently analyzed patch is ' + key_version)

            # taken from the last few lines of __init__ in LinuxMailCharacteristics
            maintainers_object = maintainers_version[key_version]

            subsystems = maintainers_object.get_subsystems_by_files(patch.diff.affected)

            # GETTING NORMALIZED PASTA MAINTAINERS START

            pasta_maintainers = list()
            for subsystem in subsystems:
                retrieved = maintainers_object.get_maintainers(subsystem)

                # retrieved structure: tuple of three: set x list x list
                # set is simply being appended to the temporary list
                for x in retrieved[0]:
                    '''from what I've seen these things are either 'moderated list' or
                    'open list', but no way of telling which
                    therefore I leave the status and the subsystem in these cases out entirely
                    explicitely no subsystem here although I could. Makes the comparison easier, since the pl data
                    doesn't have a subsystem defined in these lists here
                    '''
                    # trimming x to remove bothersome whitespaces disrupting the comparison
                    tuple = (x.strip(), "", "")

                    if tuple not in pasta_maintainers:
                        # no subsystem needed for those cases
                        pasta_maintainers.append(tuple)

                for maintain_tuple in retrieved[1]:
                    # appending it in the same structure the perl script generates
                    linuxSubsys_obj = maintainers_object[subsystem]

                    if len(linuxSubsys_obj.status) != 1:
                        # Idk in which cases there are no or more than one status, so I made this thing here and just took the first element for now
                        log.error(
                            "IMPORTANT: had more than one status or none? Lookup maintain_tuple " + str(maintain_tuple)
                            + " in retrieved " + str(retrieved))

                    # TODO: prolly unfinshed, lookup more examples later
                    # the Status enum doesn't precicely have the structure provided by get_maintainers.pl, must be minorly adjusted
                    status = linuxSubsys_obj.status[0]
                    if status is LinuxSubsystem.Status.Maintained:
                        status = "maintainer"

                    elif status is LinuxSubsystem.Status.Supported:
                        status = "supporter"

                    else:
                        status = str(status)

                    to_be_appended = ((maintain_tuple[0] + "<" + maintain_tuple[1] + ">").strip(), status, subsystem)

                    if to_be_appended != linusTorvaldsTuple:
                        pasta_maintainers.append(to_be_appended)

                for maintain_tuple in retrieved[2]:
                    log.error(
                        "THIRD LIST WASN'T EMPTY, LOOKUP SUBSYSTEM " + str(subsystem) + " was: " + str(maintain_tuple))
            # /NORMALIZED PASTA MAINTAINERS END

            log.info("maintainers successfully retrieved by PaStA")

            tempMailPath = tempfile.mkdtemp()

            # returns a set of mailinglists, pop the first element
            mailbox_listaddr = repo.mbox.message_id_to_lists[message_id].pop()
            # find the index of the next element in repo.mbox.pub_in where the listaddr matches the found mailbox
            mailbox_index = repo.mbox.pub_in.index(next((x for x in repo.mbox.pub_in if x.listaddr == mailbox_listaddr)
                                                        , None))
            # returns multiple hashes, TODO: is it ok to have the first element hardcoded?
            message_hash = repo.mbox.pub_in[mailbox_index].get_hashes(message_id)[0]

            with open(os.path.join(tempMailPath, "m"), "wb+") as f:
                f.write(repo.mbox.pub_in[mailbox_index].get_blob(message_hash))

            os.chdir(fakeLinuxPath)
            pl_output = subprocess.run(
                ['perl ' + os.path.join(fakeLinuxPath, os.path.join("scripts", "get_maintainer.pl")) + ' '
                 + str(os.path.join(tempMailPath, "m"))
                 + ' --subsystem --status --separator , --nogit --nogit-fallback --roles --norolestats']
                , shell=True
                , stdout=subprocess.PIPE).stdout.decode("utf-8")

            if pl_output == "":
                log.error("perl script did not deliver any sort of output, nothing to compare. Exiting")
                return

            # NORMALIZE PL DATA

            '''
            aim of this part of code: bring the big string of get_maintainers.pl into the form of a list of tupels
            tupels being: name <mail> | mail; status; Subsystem
            status such as 'supported' or 'maintained'

            pl_output is in form of: (element), (element)\n...alive in reporters\n[subsystemlist]
            We don't care for the last two lines, we only consider the first line with comma separated values
            '''
            pl_element_strings = pl_output.split('\n')[0].split(',')
            pl_maintainers = list()

            # TODO: this string juggling seems a bit hanky, see if you can extract the info in a more elegant way
            for pl_element in pl_element_strings:
                '''
                pl_element has the following structure: name <mail> (status:subsystem)
                I want to extract the name+mail, the status and the subsystem inside a tuple for later comparison
                '''

                # works on the assumption that the first ( in the string is the one starting the subsystem string
                maint_splitParanth = pl_element.split('(')
                name = maint_splitParanth[0]

                # special case open and moderated list, where we don't consider the status or the subsystem
                # TODO: more elegantly? like perhaps a set of strings and any of set x in maintain_line?
                # TODO: should we still consider the subsystem in case of moderated list?
                if '(open list)' in pl_element or 'moderated list' in pl_element:
                    pl_maintainers.append((name.strip(), "", ""))
                    continue

                else:
                    # works on the assumption that after the first ( and in between the first: there's the status
                    status = maint_splitParanth[1].split(":")[0]
                    # cut from after the first occurence of : till before the last character, that is )
                    subsystem = pl_element[pl_element.find(':') + 1: len(pl_element) - 1]

                # trimming x to remove bothersome whitespaces disrupting the comparison
                pl_maintainers.append((name.strip(), status, subsystem))

            # /NORMALIZE PL DATA END

            log.info("Comparing pasta and pl output for message-id: " + message_id)

            # important: pasta_maintainers is being modified through this method. Cannot be used the same way afterwards

            # STARTING COMPARISON OF PL AND PASTA
            # TODO: lots of hanky code for now, look if you can solve it in a more elegant way

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