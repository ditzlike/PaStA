"""
PaStA - Patch Stack Analysis
Copyright (c) Bayerische Motoren Werke Aktiengesellschaft (BMW AG), 2020
Copyright (c) OTH Regensburg, 2019-2020
Authors:
  Basak Erdamar <basakerdamar@gmail.com>
This work is licensed under the terms of the GNU GPL, version 2. See
the COPYING file in the top-level directory.
"""

import sys
import os
import pygit2

from csv import writer
from logging import getLogger
from argparse import ArgumentParser
from multiprocessing import Pool, cpu_count

sys.path.insert(0,os.path.abspath(os.path.join(os.path.dirname(__file__),'..')))

from pypasta.LinuxMaintainers import LinuxMaintainers
from pypasta.Util import file_to_string

log = getLogger(__name__[-15:])

# We need this global variable, as pygit2 Commit.tree objects are not pickleable
_tmp_tree = None

def flatten(nested_list):
    return [item for sublist in nested_list for item in sublist]

def walk_commit_tree(tree):
    results = []
    for entry in tree:
        if type(entry) == pygit2.Blob:
            results.append(entry.name)
        elif type(entry) == pygit2.Tree:
            results += [os.path.join(entry.name, item)
                        for item in walk_commit_tree(entry)]
    return results

def get_tree(repo, revision):
    if revision != '':
        try:
            if revision.startswith('v'):
                revision = repo.lookup_reference('refs/tags/%s' % revision).target
            commit_hash = repo[revision].target
            tree = repo[commit_hash].tree
        except ValueError:
            raise
    else:
        commit = repo.revparse_single(repo.head.name)
        tree = commit.tree
    return tree

def decreasing_order(dictionary):
    return sorted(dictionary.items(), key=lambda item:item[1].loc, reverse=True)

def read_file(filename):
    return _tmp_tree[filename].data.decode('iso8859')

def get_filesize(filename):
    f = read_file(filename)
    try:
        return (filename, (f.count('\n'), len(f)))
    # Empty file:
    except:
        return (filename, (0, 0))

def get_excluded_dirs(larger_set_dirs, filter_set_dirs):
    for item in larger_set_dirs.copy():
        for item_filt in filter_set_dirs:
            if os.path.commonpath([item_filt, item]):
                larger_set_dirs.remove(item)
                # No need to check for other items in the smaller set
                break
    return reduce_dirs(larger_set_dirs)

def reduce_dirs(set_of_directories):
    if len(set_of_directories) < 2:
        return set_of_directories
    # If there is only one common path in the set, return it
    results = os.path.commonpath(set_of_directories)
    if results:
        return [results]
    # Otherwise filter out directories that are subdirectories of other
    # elements in the set, return the filtered set
    results = sorted(set_of_directories, key=len)
    for index, dir_name in enumerate(results):
        for subdirname in results[index:]:
            if os.path.commonpath([dir_name, subdirname]) == dir_name:
                results.remove(subdirname)
    return results

def pretty_name(maintainer):
    return maintainer[0]+' <'+maintainer[1]+'>'

def status(all_maintainers, subsystem_name):
    if any(all_maintainers.subsystems[subsystem_name].status):
        return all_maintainers.subsystems[subsystem_name].status[0].value
    else:
        return ''

class CountItem :
    def __init__(self, filename, loc, byte, filter):
        self.loc = loc
        self.byte = byte
        if filter:
            self.loc_filt = self.loc
            self.byte_filt = self.byte
        else:
            self.loc_filt = self.byte_filt = 0
    def increase(self, filename, loc, byte, filter):
        self.loc += loc
        self.byte += byte
        if filter:
            self.loc_filt += loc
            self.byte_filt += byte
    def display_in_filter(self):
        # whether to show this item in filtered view or not
        if self.loc_filt > 0:
            return True
        return False

def get_counts_by_entry(all_maintainers, file_sizes, filter_by_files = None):
    counts = dict()
    containing_dirs = dict()
    containing_dirs_filt = dict()
    for filename in file_sizes:
        subsystems = all_maintainers.get_subsystems_by_file(filename)
        for subsystem in subsystems:
            loc, byte = file_sizes[filename]
            directory = os.path.dirname(filename)
            if subsystem in counts:
                counts[subsystem].increase(filename, loc, byte,
                                filter_by_files and filename in filter_by_files)
            else:
                counts[subsystem] = CountItem(filename, loc, byte,
                                filter_by_files and filename in filter_by_files)
                # If the subsystem is not already included in the directories
                # dictionary, we will have to first initialize as an empty set
                # and then add the directory
                containing_dirs[subsystem] = set()
            containing_dirs[subsystem].add(directory)
            # If the file is in filter too, we add the directory to the filtered
            # dictionary as well
            if filter_by_files and filename in filter_by_files:
                if not subsystem in containing_dirs_filt:
                    containing_dirs_filt[subsystem] = set()
                containing_dirs_filt[subsystem].add(directory)
    if filter_by_files:
        # If filter is given, only return the relevant lines:
        counts = {name:item for name,item in counts.items()
                    if item.display_in_filter()}
        # Get the directories excluded in filter list for each subsystem in
        # filtered list : IRRELEVANT
        containing_dirs = {
            key: get_excluded_dirs(containing_dirs[key], value)
            for key, value in containing_dirs_filt.items()}
        containing_dirs_filt = {key:reduce_dirs(value)
            for key, value in containing_dirs_filt.items()}
    # Sort subsystems by decreasing total line counts
    return decreasing_order(counts), containing_dirs, containing_dirs_filt

def get_counts_by_maintainer(all_maintainers, file_sizes,
                                verbose, filter_by_files = None):
    maintainer_to_subsystem = dict()
    # maps maintainers to total file sizes they are responsible for
    counts = dict()
    for filename in file_sizes:
        subsystems = all_maintainers.get_subsystems_by_file(filename)
        for subsystem in subsystems:
            maintainers = all_maintainers.get_maintainers(subsystem)
            for maintainer in flatten(maintainers):
                if not (type(maintainer) == str
                        or maintainer[0] == ''
                        or maintainer[1] == ''):
                    name = pretty_name(maintainer)
                    loc, byte = file_sizes[filename]
                    if name in counts:
                        maintainer_to_subsystem[name].add(subsystem)
                        counts[name].increase(filename, loc, byte,
                                filter_by_files and filename in filter_by_files)
                    else:
                        maintainer_to_subsystem[name] = set([subsystem])
                        counts[name] = CountItem(filename, loc, byte,
                                filter_by_files and filename in filter_by_files)
                elif verbose:
                    log.info('Ignoring mailing list:'+ str(maintainer))
    if filter_by_files:
        # If filter is given, only return the relevant lines:
        counts = {name:item for name,item in counts.items()
                    if item.display_in_filter()}
    # Sort maintainers by decreasing total line counts
    return decreasing_order(counts), maintainer_to_subsystem

def show_maintainers(config, sub, argv):
    parser = ArgumentParser(description='Display file sizes grouped by '
                                            'maintainers or subsystems')
    parser.add_argument('show_maintainers', nargs=1, type=bool)
    parser.add_argument('--entries', action='store_true',
                            help='groups by subsystems')
    parser.add_argument('--verbose', action='store_true',
                            help='Show ignored exceptions on the way')
    parser.add_argument('--smallstat', action='store_true', help='Simple view')
    parser.add_argument('--bytes', action='store_true', help='Show byte counts')
    parser.add_argument('--outfile', type=str, help='Output to a csv file')
    parser.add_argument('--filter', type=str, help='Filter by file list: '
                        'enter the file name for the file containing the list '
                        'of files to filter by.')
    parser.add_argument('--revision', type=str, help='Specify a commit hash or '
                        'a version name for a Linux repo')

    args = parser.parse_args()

    if args.filter:
        filter_by_files = file_to_string(args.filter).splitlines()

    d_repo = config.repo_location
    repo = config.repo.repo

    if  args.revision != None:
        version = args.revision
    elif args.filter:
        version = '.'.join(args.filter.split('.')[1:3])
    else:
        version = ''
    tree = get_tree(repo, version)

    all_filenames = walk_commit_tree(tree)
    all_maintainers = LinuxMaintainers(tree['MAINTAINERS'].data.decode('iso8859'))

    global _tmp_tree
    _tmp_tree = tree

    processes = int(cpu_count())
    p = Pool(processes=processes, maxtasksperchild=1)
    result = p.map(get_filesize, all_filenames)
    p.close()
    p.join()

    file_sizes = dict(result)

    _tmp_tree = None

    if args.entries:
        title = ['Entries']
        if args.filter != None:
            counts, irrelevant_dirs, relevant_dirs = get_counts_by_entry(
                all_maintainers, file_sizes, filter_by_files)
        else:
            counts, _, _= get_counts_by_entry(all_maintainers, file_sizes)
    else:
        title = ['Maintainers']
        if args.filter != None:
            counts, maintainer_to_subsystem = get_counts_by_maintainer(
                all_maintainers, file_sizes, args.verbose, filter_by_files)
        else:
            counts, maintainer_to_subsystem = get_counts_by_maintainer(
                all_maintainers, file_sizes, args.verbose)

    fields = dict()
    fields['Maintainers'] = fields['Entries'] = lambda item : item[0]
    fields['LoC in list'] = lambda item : item[1].loc_filt
    fields['Total LoC'] = fields['LoC'] = lambda item : item[1].loc
    fields['Byte count'] = lambda item : item[1].byte
    fields['In list(%)']=lambda item:round((item[1].loc_filt/item[1].loc)*100,2)
    fields['Status'] = lambda item : status(all_maintainers, item[0])
    fields['Entries of maintainer']=lambda item:', '.join(maintainer_to_subsystem[item[0]])
    fields['Irrelevant directories'] = lambda item: ', '.join(irrelevant_dirs[item[0]])
    fields['Relevant directories'] = lambda item: ', '.join(relevant_dirs[item[0]])

    title.append('LoC')
    if args.bytes:
        title += ['Byte count']
    if not args.smallstat:
        if args.filter != None:
            title += ['LoC in list', 'In list(%)']
            if args.entries:
                title += ['Irrelevant directories', 'Relevant directories']
        if args.entries:
            title.insert(1, 'Status')
        else:
            title += ['Entries of maintainer']

    results = [[fields[field](item) for field in title] for item in counts]
    results.insert(0, title)
    if args.outfile!= None:
        with open(args.outfile, 'w+') as csv_file:
            csv_writer = writer(csv_file)
            csv_writer.writerows(results)
    else:
        width = len(max(list(zip(*results))[0], key = len))
        _, columns = os.popen('stty size', 'r').read().split()
        columns = int(columns)
        for line in results:
            line_s = str(line[0]).ljust(width+4)
            for item in line[1:]:
                line_s += str(item).ljust(12)
            if len(line_s) > columns:
                print(line_s[0:columns-3]+"...")
            else:
                print(line_s)
    return 0
