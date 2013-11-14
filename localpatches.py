#!/usr/bin/python
# -*- coding: utf-8 -*-

# Given a standard third party (and free) software, like Invenio,
# detect which files are new or modified in the local instance, and
# create a simple set of patches, so they can be imported to guilt or
# quilt.

# It may be useful to other softwares.  Or not.  But sure it has to be
# adapted to them.

# Quick and dirty.  Public domain.

from __future__ import print_function, division

import os
import sys
import difflib
import fnmatch
import argparse

directories = ['bin', 'etc', 'lib', 'share']
ignore_patterns = ['*~', '*.OLD', '*.pyc', '*.rej', '*.mo', '*.html',
                   '__init__.py', 'bash_completion.d/*']


def recursive_file_gen(mydir):
    for root, dirs, files in os.walk(mydir):
        for filename in files:
            yield os.path.join(root, filename)


def ignore_file(filename, ignore_patterns=ignore_patterns):
    for pattern in ignore_patterns:
        if fnmatch.fnmatch(filename, pattern):
            return True
    return False


def basename(path):
    filename = os.path.split(path)[-1]
    return os.path.splitext(filename)[0]


def main():
    parser = argparse.ArgumentParser(
        description='Detect local modifications of a third-party software and write them as patches')

    parser.add_argument(
        '--upstream-dir',
        required=True,
        action='store',
        help='Path to the current, configured, original upstream dir')

    parser.add_argument(
        '--install-dir',
        required=True,
        action='store',
        help='Directory where your software is installed')

    parser.add_argument(
        '--output-dir',
        required=True,
        action='store',
        help='Empty directory where patches will be are written')

    args = parser.parse_args()

    if args.upstream_dir.startswith('~'):
        args.upstream_dir = os.path.expanduser(args.upstream_dir)
    if args.install_dir.startswith('~'):
        args.install_dir = os.path.expanduser(args.install_dir)
    if args.output_dir.startswith('~'):
        args.output_dir = os.path.expanduser(args.output_dir)

    for param in [args.upstream_dir, args.install_dir, args.output_dir]:
        if not os.path.isdir(param):
            print('Error: %s is not a directory' % (param),
                  file=sys.stderr)
            sys.exit(1)

    if os.listdir(args.output_dir):
        print('Error: directory %s not empty' % (args.output_dir),
              file=sys.stderr)
        sys.exit(1)

    local_files = []
    for directory in directories:
        for filename in recursive_file_gen(os.path.join(args.install_dir,
                                                        directory)):
            if not ignore_file(filename):
                local_files.append(filename)

    original_files = list(recursive_file_gen(args.upstream_dir))
    for local_file in local_files:
        filename = os.path.sep + os.path.split(local_file)[-1]
        upstream = ''
        for original_file in original_files:
            if original_file.endswith(filename):
                upstream = original_file

        if upstream:
            with open(upstream) as f:
                a = f.readlines()
        else:
            a = ''

        try:
            with open(local_file) as f:
                b = f.readlines()
        except IOError:
            print('ERROR: cannot read %s' % (local_file))
            b = ''

        if a != b:
            print('%s modified' % (local_file))
            if upstream:
                upstream = os.path.join('a', local_file)
            else:
                upstream = '/dev/null'
            local_file = os.path.join('b', local_file)
            diff = list(difflib.unified_diff(a, b,
                                             fromfile=upstream,
                                             tofile=local_file))
            filename = os.path.join(args.output_dir,
                                    basename(local_file) + '.patch')
            with open(filename, 'w') as f:
                f.write(''.join(diff))


if __name__ == '__main__':
    main()
