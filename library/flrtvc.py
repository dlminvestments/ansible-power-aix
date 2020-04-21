#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2020- IBM, Inc
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'community'}

DOCUMENTATION = r'''
---
author:
- AIX Development Team (@pbfinley1911)
module: flrtvc
short_description: Generate FLRTVC report, download and install efix.
description:
- Creates a task to check targets vulnerability against available fixes, and
  apply necessary fixes. It downloads and uses the Fix Level Recommendation Tool
  Vulnerability Checker Script to generates a report. It parses the report,
  downloads the fixes, checks their versions and if some files are locked. Then
  it installs the remaining fixes. In case of inter-locking file you could run
  this several times.
version_added: '2.8'
requirements: [ AIX ]
options:
  apar:
    description:
    - Type of APAR to check or download.
    - C(sec) Security vulnerabilities.
    - C(hiper) Corrections to High Impact PERvasive threats.
    - C(all) Same behavior as None, both C(sec) and C(hiper) vulnerabilities.
    type: str
    choices: [ sec, hiper, all, None ]
  filesets:
    description:
    - Filter filesets for specific phrase. Only fixes on the filesets specified will be checked and updated.
    type: str
  csv:
    description:
    - Path to a APAR CSV file containing the description of the C(sec) and C(hiper) fixes.
    - This file is usually transferred from the fix server; this rather big transfer
      can be avoided by specifying an already transferred file.
    type: str
  path:
    description:
    - Specifies the working directory used for temporary files. It will contain FLRTVC reports,
      previously installed filesets and fixes lists and downloaded fixes.
    type: str
    default: /var/adm/ansible/work
  verbose:
    description:
    - Generate full FLRTVC reporting (verbose mode).
    type: bool
    default: no
  force:
    description:
    - Specifies to remove currently installed ifix before running the FLRTVC script.
    type: bool
    default: no
  clean:
    description:
    - Cleanup working directory with all downloaded files at the end of execution.
    type: bool
    default: no
  check_only:
    description:
    - Specifies to only check if fixes are already applied on the targets.
      No download or install operations.
    type: bool
    default: no
  download_only:
    description:
    - Specifies to perform check and download operation, do not install anything.
    type: bool
    default: no
  increase_fs:
    description:
    - Specifies to increase filesystem size of the working directory if needed.
    type: bool
    default: yes
'''

EXAMPLES = r'''
- name: Download patches for security vulnerabilities
  flrtvc:
    path: /usr/sys/inst.images
    verbose: yes
    apar: sec
    download_only: yes

- name: Install both sec and hyper patches for all filesets starting with devices.fcp
  flrtvc:
    path: /usr/sys/inst
    filesets: devices.fcp.*
    verbose: yes
    force: no
    clean: no
'''

RETURN = r'''
meta:
    description: Detailed information on the module execution.
    returned: always
    type: dict
    contains:
        messages:
            description: Details on errors/warnings
            returned: always
            type: list
            elements: str
            sample:
        0.report:
            description: Output of the FLRTVC script, report or details on flrtvc error if any.
            returned: if the FLRTVC script run succeeds
            type: list
            elements: str
            sample: see below
        1.parse:
            description: List of URLs to download or details on parsing error if any.
            returned: if the parsing succeeds
            type: list
            elements: str
            sample: see below
        2.discover:
            description: List of epkgs found in URLs.
            returned: if the discovery succeeds
            type: list
            elements: str
            sample: see below
        3.download:
            description: List of downloaded epkgs.
            returned: if download succeeds
            type: list
            elements: str
            sample: see below
        4.1.reject:
            description: List of epkgs rejected, refer to messages and log file for reason.
            returned: if check succeeds
            type: list
            elements: str
            sample: see below
        4.2.check:
            description: List of epkgs following prerequisites.
            returned: if check succeeds
            type: list
            elements: str
            sample: see below
        5.install:
            description: List of epkgs actually installed.
            returned: if install succeeds
            type: list
            elements: str
            sample: see below
    sample:
        "meta": {
            "0.report": [
                "Fileset|Current Version|Type|EFix Installed|Abstract|Unsafe Versions|APARs|Bulletin URL|Download URL|CVSS Base Score|Reboot Required|
                 Last Update|Fixed In",
                "bos.net.tcp.client_core|7.2.3.15|sec||NOT FIXED - There is a vulnerability in FreeBSD that affects AIX.|7.2.3.0-7.2.3.15|
                 IJ09625 / CVE-2018-6922|http://aix.software.ibm.com/aix/efixes/security/freebsd_advisory.asc|\
                 ftp://aix.software.ibm.com/aix/efixes/security/freebsd_fix.tar|CVE-2018-6922:7.5|NO|11/08/2018|7200-03-03",
                ...,
            ],
            "1.parse": [
                "ftp://aix.software.ibm.com/aix/efixes/security/ntp_fix12.tar",
                "ftp://aix.software.ibm.com/aix/efixes/security/tcpdump_fix4.tar",
                ...,
            ],
            "2.discover": [
                "ntp_fix12/IJ17059m9b.190719.epkg.Z",
                "ntp_fix12/IJ17060m9a.190628.epkg.Z",
                ...,
                "tcpdump_fix4/IJ12978s9a.190215.epkg.Z",
                "tcpdump_fix4/IJ12978sBa.190215.epkg.Z",
                ...,
            ],
            "3.download": [
                "/usr/sys/inst.images/tardir/ntp_fix12/IJ17059m9b.190719.epkg.Z",
                "/usr/sys/inst.images/tardir/ntp_fix12/IJ17060m9a.190628.epkg.Z",
                ...,
                "/usr/sys/inst.images/tardir/tcpdump_fix4/IJ12978s9a.190215.epkg.Z",
                "/usr/sys/inst.images/tardir/tcpdump_fix4/IJ12978sBa.190215.epkg.Z",
                ...,
            ],
            "4.1.reject": [
                "102p_fix: prerequisite openssl.base levels do not match: 1.0.2.1600 < 1.0.2.1500 < 1.0.2.1600",
                ...,
                "IJ12983m2a: locked by previous efix to install",
                ...,
                "IJ17059m9b: prerequisite missing: ntp.rte",
                ...,
            ],
            "4.2.check": [
                "/usr/sys/inst.images/tardir/tcpdump_fix5/IJ20785s2a.191119.epkg.Z",
                ...,
            ],
            "5.install": [
                "/usr/sys/inst.images/tardir/tcpdump_fix5/IJ20785s2a.191119.epkg.Z",
                ...,
            ],
            "messages": [
                "a previous efix to install will lock a file of IJ20785s3a preventing its installation, install it manually or run the task again.",
                ...,
            ]
        }
'''

import logging
import os
import re
import csv
import threading
import urllib
import ssl
import shutil
import tarfile
import zipfile
import stat
import time
import calendar

from collections import OrderedDict
from ansible.module_utils.basic import AnsibleModule

module = None
results = None
workdir = ""

# Threading
THRDS = []


def start_threaded(thds):
    """
    Decorator for thread start
    """
    def start_threaded_wrapper(func):
        """
        Decorator wrapper for thread start
        """
        def start_threaded_inner_wrapper(*args):
            """
            Decorator inner wrapper for thread start
            """
            thd = threading.Thread(target=func, args=args)
            logging.debug('Start thread {}'.format(func.__name__))
            thd.start()
            thds.append(thd)
        return start_threaded_inner_wrapper
    return start_threaded_wrapper


def wait_threaded(thds):
    """
    Decorator for thread join
    """
    def wait_threaded_wrapper(func):
        """
        Decorator wrapper for thread join
        """
        def wait_threaded_inner_wrapper(*args):
            """
            Decorator inner wrapper for thread join
            """
            func(*args)
            for thd in thds:
                thd.join()
        return wait_threaded_inner_wrapper
    return wait_threaded_wrapper


def logged(func):
    """
    Decorator for logging
    """
    def logged_wrapper(*args):
        """
        Decorator wrapper for logging
        """
        logging.debug('ENTER {} with {}'.format(func.__name__, args))
        res = func(*args)
        logging.debug('EXIT {} with {}'.format(func.__name__, res))
        return res
    return logged_wrapper


@logged
def download(src, dst, resize_fs=True):
    """
    Download efix from url to directory
    args:
        src       (str): The url to download
        dst       (str): The absolute destination filename
        resize_fs (bool): Increase the filesystem size if needed
    return:
        True if download succeeded
        False otherwise
    """
    res = True
    wget = '/bin/wget'
    if not os.path.isfile(dst):
        logging.debug('downloading {} to {}...'.format(src, dst))
        if os.path.exists(wget):
            cmd = [wget, '--no-check-certificate', src, '-P', os.path.dirname(dst)]
            rc, stdout, stderr = module.run_command(cmd)
            if rc == 3:
                if resize_fs and increase_fs(dst):
                    os.remove(dst)
                    return download(src, dst, resize_fs)
            elif rc != 0:
                msg = 'Cannot download {}'.format(src)
                logging.error(msg)
                logging.error('cmd={} rc={} stdout:{} stderr:{}'
                              .format(cmd, rc, stdout, stderr))
                results['meta']['messages'].append(msg)
                res = False
        else:
            msg = 'Cannot locate {}, please install related package.'.format(wget)
            logging.error(msg)
            results['meta']['messages'].append(msg)
            res = False
    else:
        logging.debug('{} already exists'.format(dst))
    return res


@logged
def unzip(src, dst, resize_fs=True):
    """
    Unzip source into the destination directory
    args:
        src       (str): The url to unzip
        dst       (str): The absolute destination path
        resize_fs (bool): Increase the filesystem size if needed
    return:
        True if unzip succeeded
        False otherwise
    """
    try:
        zfile = zipfile.ZipFile(src)
        zfile.extractall(dst)
    except (zipfile.BadZipfile, zipfile.LargeZipFile, RuntimeError) as exc:
        if resize_fs and increase_fs(dst):
            return unzip(src, dst)
        else:
            msg = 'Cannot unzip {}'.format(src)
            logging.error(msg)
            logging.error('EXCEPTION {}'.format(exc))
            results['meta']['messages'].append(msg)
            return False
    return True


@logged
def remove_efix():
    """
    Remove efix matching the given label
    return:
        True if remove succeeded
        False otherwise
    """
    res = True
    logging.debug('Removing all installed efix')

    # List epkg on the system
    cmd = ['/usr/sbin/emgr', '-P']
    rc, stdout, stderr = module.run_command(cmd, use_unsafe_shell=True)
    if rc != 0:
        msg = 'Cannot list interim fix to remove'
        logging.error(msg)
        logging.error('cmd:{} failed rc={} stdout:{} stderr:{}'
                      .format(cmd, rc, stdout, stderr))
        results['meta']['messages'].append('{}: {}'.format(msg, stderr))
        return False

    # Create a list of unique epkg label
    # stdout is either empty (if there is no epkg data on the system) or contains
    # the following
    # PACKAGE                                                  INSTALLER   LABEL
    # ======================================================== =========== ==========
    # X11.base.rte                                             installp    IJ11547s0a
    # bos.net.tcp.client_core                                  installp    IJ09623s2a
    # bos.perf.perfstat                                        installp    IJ09623s2a
    epkgs = [epkg.strip().split()[-1] for epkg in stdout.strip().splitlines()]
    if len(epkgs) >= 2:
        del epkgs[0:2]
    epkgs = list(set(epkgs))

    # Remove each epkg from their label
    for epkg in epkgs:
        cmd = ['/usr/sbin/emgr', '-r', '-L', epkg]
        rc, stdout, stderr = module.run_command(cmd)
        for line in stdout.strip().splitlines():
            match = re.match(r'^\d+\s+(\S+)\s+REMOVE\s+(\S+)\s*$', line)
            if match:
                if 'SUCCESS' in match.group(2):
                    msg = 'efix {} removed, please check if you want to reinstall it'\
                          .format(match.group(1))
                    logging.info(msg)
                    results['meta']['messages'].append(msg)
                else:
                    msg = 'Cannot remove efix {}, see logs for details'.format(match.group(1))
                    logging.error(msg)
                    results['meta']['messages'].append(msg)
                    res = False
    return res


def to_utc_epoch(date):
    """
    Return the time (UTC time zone) in second from unix epoch (int)

    args:
        date (str) : time to convert in sec from epoch with the format:
                     'Mon Oct 9 23:35:09 CDT 2017'
    returns: (epoch, msg)
        The value in sec from epoch , ''
        -1,  'error message in case of error'
    """

    TZ = 'UTC'
    msg = ''
    sec_from_epoch = -1
    # supported TZ translation
    shift = {'CDT': -5, 'CEST': 2, 'CET': 1, 'CST': -6, 'CT': -6,
             'EDT': -4, 'EET': 2, 'EST': -5, 'ET': -5,
             'IST': 5.5,
             'JST': 9,
             'MSK': 3, 'MT': 2,
             'NZST': 12,
             'PDT': -7, 'PST': -8,
             'SAST': 2,
             'UTC': 0,
             'WEST': 1, 'WET': 0}

    # if no time zone, consider it's UTC
    match = re.match(r'^(\S+\s+\S+\s+\d+\s+\d+:\d+:\d+)\s+(\d{4})$', date)
    if match:
        date = '{} UTC {}'.format(match.group(1), match.group(2))
    else:
        match = re.match(r'^(\S+\s+\S+\s+\d+\s+\d+:\d+:\d+)\s+(\S+)\s+(\d{4})$', date)
        if match:
            date = '{} UTC {}'.format(match.group(1), match.group(3))
            TZ = match.group(2)
        else:  # should not happen
            return (-1, 'bad packaging date format')

    try:
        datet = time.strptime(date, "%a %b %d %H:%M:%S %Z %Y")
        sec_from_epoch = calendar.timegm(datet)
    except ValueError:
        return (-1, 'EXCEPTION: cannot parse packaging date')

    if TZ not in shift:
        msg = 'Unsuported Time Zone: "TZ", using "UTC"'
        TZ = 'UTC'

    sec_from_epoch = sec_from_epoch - (shift[TZ] * 3600)

    return (sec_from_epoch, msg)


@logged
def check_epkgs(epkg_list, lpps, efixes):
    """
    For each epkg get the label, packaging date, filset and check prerequisites
    based on fileset current level and build a list ordered by packaging date
    that should not be locked at its installation.

    Note: in case of parsing error, keep the epkg (best effort)

    args:
        epkg_list (list): The list of efixes to check
        lpps      (dict): The current lpps levels
        efixes    (dict): The current efixes info
    returns:
        The list of epkg to install (ordered by packaging date)
        The list of epkg to rejected with the reason (ordered by label)
    """

    epkgs_info = {}
    epkgs_reject = []

    # Installed efix could lock some files we will try to modify,
    # let's build a dictionary indexed upon file location
    locked_files = {}
    for efix in efixes:
        for file in efixes[efix]['files']:
            if file not in locked_files:
                locked_files[file] = efix
    logging.debug('locked_files: {}'.format(locked_files))

    # Get information on efix we want to install and check it can be installed
    for epkg_path in epkg_list:
        epkg = {'path': epkg_path,
                'label': '',
                'pkg_date': None,
                'sec_from_epoch': -1,
                'filesets': [],
                'files': [],
                'prereq': {},
                'reject': False}

        # get efix information
        stdout = ''
        cmd = '/usr/sbin/emgr -dXv3 -e {} | /bin/grep -p -e PREREQ -e PACKAG'\
              .format(epkg['path'])
        rc, stdout, stderr = module.run_command(cmd, use_unsafe_shell=True)
        if rc != 0:
            msg = 'Cannot get efix information {}'.format(epkg['path'])
            logging.error(msg)
            logging.error('cmd:{} failed rc={} stdout:{} stderr:{}'
                          .format(cmd, rc, stdout, stderr))
            results['meta']['messages'].append(msg)
            # do not break or continue, we keep this efix, will try to install it anyway

        # ordered parsing: expecting the following line order:
        # LABEL, PACKAGING DATE, then PACKAGE, then prerequisites levels
        for line in stdout.splitlines():
            # skip comments and empty lines
            line = line.rstrip()
            if not line or line.startswith('+'):
                continue  # skip blank and comment line

            if not epkg['label']:
                # match: "LABEL:            IJ02726s8a"
                match = re.match(r'^LABEL:\s+(\S+)$', line)
                if match:
                    epkg['label'] = match.group(1)
                    continue

            if not epkg['pkg_date']:
                # match: "PACKAGING DATE:   Mon Oct  9 09:35:09 CDT 2017"
                match = re.match(r'^PACKAGING\s+DATE:\s+'
                                 r'(\S+\s+\S+\s+\d+\s+\d+:\d+:\d+\s+\S*\s*\S+).*$',
                                 line)
                if match:
                    epkg['pkg_date'] = match.group(1)
                    continue

            # match: "   PACKAGE:       devices.vdevice.IBM.vfc-client.rte"
            match = re.match(r'^\s+PACKAGE:\s+(\S+)\s*?$', line)
            if match:
                if match.group(1) not in epkg['filesets']:
                    epkg['filesets'].append(match.group(1))
                continue

            # match: "   LOCATION:      /usr/lib/boot/unix_64"
            match = re.match(r'^\s+LOCATION:\s+(\S+)\s*?$', line)
            if match:
                if match.group(1) not in epkg['files']:
                    epkg['files'].append(match.group(1))
                continue

            # match and convert prerequisite levels
            # line like: "bos.net.tcp.server 7.1.3.0 7.1.3.49"
            match = re.match(r'^(\S+)\s+([\d+\.]+)\s+([\d+\.]+)\s*?$', line)
            if match is None:
                continue
            (prereq, minlvl, maxlvl) = match.groups()
            epkg['prereq'][prereq] = {}
            epkg['prereq'][prereq]['minlvl'] = minlvl
            epkg['prereq'][prereq]['maxlvl'] = maxlvl

            # parsing done
            # check filseset prerequisite is present
            if prereq not in lpps:
                epkg['reject'] = '{}: prerequisite missing: {}'.format(os.path.basename(epkg['path']), prereq)
                logging.info('reject {}'.format(epkg['reject']))
                break  # stop parsing

            # check filseset prerequisite is present
            minlvl_i = list(map(int, epkg['prereq'][prereq]['minlvl'].split('.')))
            maxlvl_i = list(map(int, epkg['prereq'][prereq]['maxlvl'].split('.')))
            if lpps[prereq]['int'] < minlvl_i\
               or lpps[prereq]['int'] > maxlvl_i:
                epkg['reject'] = '{}: prerequisite {} levels do not match: {} < {} < {}'\
                                 .format(os.path.basename(epkg['path']),
                                         prereq,
                                         epkg['prereq'][prereq]['minlvl'],
                                         lpps[prereq]['str'],
                                         epkg['prereq'][prereq]['maxlvl'])
                logging.info('reject {}'.format(epkg['reject']))
                break
        if epkg['reject']:
            epkgs_reject.append(epkg['reject'])
            continue

        # check file locked by efix already installed
        for file in epkg['files']:
            if file in locked_files:
                results['meta']['messages'].append('installed efix {} is locking {} preventing the '
                                                   'installation of {}, remove it manually or set the '
                                                   '"force" option.'
                                                   .format(locked_files[file], file, os.path.basename(epkg['path'])))
                epkg['reject'] = '{}: installed efix {} is locking {}'\
                                 .format(os.path.basename(epkg['path']), locked_files[file], file)
                logging.info('reject {}'.format(epkg['reject']))
                epkgs_reject.append(epkg['reject'])
                continue
        if epkg['reject']:
            continue

        # convert packaging date into time in sec from epoch

        if epkg['pkg_date']:
            (sec_from_epoch, msg) = to_utc_epoch(epkg['pkg_date'])
            if sec_from_epoch == -1:
                logging.error('{}: "{}" for epkg:{} '
                              .format(msg, epkg['pkg_date'], epkg))
            epkg['sec_from_epoch'] = sec_from_epoch

        epkgs_info[epkg['path']] = epkg.copy()

    # sort the epkg by packing date (sec from epoch)
    sorted_epkgs = OrderedDict(sorted(epkgs_info.items(),
                                      key=lambda t: t[1]['sec_from_epoch'],
                                      reverse=True)).keys()

    # exclude epkg that will be interlocked
    global_file_locks = []
    removed_epkg = []
    for epkg in sorted_epkgs:
        if set(epkgs_info[epkg]['files']).isdisjoint(set(global_file_locks)):
            global_file_locks.extend(epkgs_info[epkg]['files'])
            logging.info('keep {}, files: {}'
                         .format(os.path.basename(epkgs_info[epkg]['path']), epkgs_info[epkg]['files']))
        else:
            results['meta']['messages'].append('a previous efix to install will lock a file of {} '
                                               'preventing its installation, install it manually or '
                                               'run the task again.'
                                               .format(os.path.basename(epkgs_info[epkg]['path'])))
            epkgs_info[epkg]['reject'] = '{}: locked by previous efix to install'\
                                         .format(os.path.basename(epkgs_info[epkg]['path']))
            logging.info('reject {}'.format(epkgs_info[epkg]['reject']))
            epkgs_reject.append(epkgs_info[epkg]['reject'])
            removed_epkg.append(epkg)
    for epkg in removed_epkg:
        sorted_epkgs.remove(epkg)

    epkgs_reject = sorted(epkgs_reject)  # order the reject list by label

    return (sorted_epkgs, epkgs_reject)


@logged
def parse_lpps_info():
    """
    Parse the lslpp file and build a dictionary with installed lpps current levels
    returns:
        The list of epkg to install (ordered by packaging date)
    """
    global workdir

    lpps_lvl = {}
    lslpp_file = os.path.join(workdir, 'lslpp.txt')

    with open(os.path.abspath(lslpp_file), 'r') as myfile:
        for myline in myfile:
            # beginning of line: "bos:bos.rte:7.1.5.0: : :C: :Base Operating System Runtime"
            mylist = myline.split(':')
            if len(mylist) < 3:
                msg = 'file {} is malformed'.format(lslpp_file)
                logging.error('{}: got line: "{}"'.format(msg, myline))
                results['meta']['messages'].append(msg)
                continue
            lpps_lvl[mylist[1]] = {'str': mylist[2]}
            mylist[2] = re.sub(r'-', '.', mylist[2])
            lpps_lvl[mylist[1]]['int'] = list(map(int, mylist[2].split('.')))

    return lpps_lvl


@start_threaded(THRDS)
@logged
def run_lslpp(filename):
    """
    Use lslpp on a target system to list filesets and write into provided file.
    args:
        filename (str): The filename to store output
    return:
        True if lslpp succeeded
        False otherwise
    """
    logging.debug('{}'.format(filename))
    cmd = ['/bin/lslpp', '-Lcq']
    logging.debug('run cmd="{}"'.format(' '.join(cmd)))
    rc, stdout, stderr = module.run_command(cmd)

    if rc == 0:
        with open(filename, 'w') as myfile:
            myfile.write(stdout)
        return True
    else:
        msg = 'Failed to list fileset'
        logging.error(msg)
        logging.error('cmd:{} failed rc={}'.format(cmd, rc))
        logging.error('stdout:{}'.format(stdout))
        logging.error('stderr:{}'.format(stderr))
        return False


@logged
def parse_emgr():
    """
    Parse the emgr file and build a dictionary with efix data
    return:
        The dictionary with efixe data as the following structure:
            efixes[label]['files'][file]
            efixes[label]['packages'][package]
    """
    global workdir

    efixes = {}
    emgr_file = os.path.join(workdir, 'emgr.txt')
    label = ''
    file = ''
    package = ''

    with open(os.path.abspath(emgr_file), 'r') as myfile:
        for line in myfile:
            line = line.rstrip()
            if not line or line.startswith('+') or line.startswith('='):
                continue

            # "EFIX ID: 1" triggers a new efix
            match_key = re.match(r"^EFIX ID:\s+\S+$", line)
            if match_key:
                label = ''
                file = ''
                package = ''
                continue

            if not label:
                match_key = re.match(r"^EFIX LABEL:\s+(\S+)$", line)
                if match_key:
                    label = match_key.group(1)
                    efixes[label] = {}
                    efixes[label]['files'] = {}
                    efixes[label]['packages'] = {}
                continue

            # "   LOCATION:      /usr/sbin/tcpdump" triggers a new file
            match_key = re.match(r"^\s+LOCATION:\s+(\S+)$", line)
            if match_key:
                package = ''
                file = match_key.group(1)
                efixes[label]['files'][file] = file
                continue

            # "   PACKAGE:            bos.net.tcp.client
            match_key = re.match(r"^\s+PACKAGE:\s+(\S+)$", line)
            if match_key:
                file = ''
                package = match_key.group(1)
                efixes[label]['packages'][package] = package
                continue

    return efixes


@start_threaded(THRDS)
@logged
def run_emgr(f_efix):
    """
    Use the interim fix manager to list detailed information of
    installed efix and locked packages on the target machine
    and write into provided file.
    args:
        f_efix       (str): The filename to store output of emgr -lv3
        f_locked_pkg (str): The filename to store output of emgr -P
    return:
        True if emgr succeeded
        False otherwise
    """

    # list efix information
    cmd = ['/usr/sbin/emgr', '-lv3']
    logging.debug('run cmd="{}"'.format(' '.join(cmd)))
    rc, stdout, stderr = module.run_command(cmd)
    if rc == 0:
        with open(f_efix, 'w') as myfile:
            myfile.write(stdout)
        return True
    else:
        msg = 'Failed to list interim fix information'
        logging.error(msg)
        logging.error('cmd:{} failed rc={}'.format(cmd, rc))
        logging.error('stdout:{}'.format(stdout))
        logging.error('stderr:{}'.format(stderr))
        return False


@logged
def run_flrtvc(flrtvc_path, params, force):
    """
    Use the flrtvc script on target system to get the
    args:
        flrtvc_path (str): The path to the flrtvc script to run
        params     (dict): The parameters to pass to flrtvc command
        force      (bool): The flag to automatically remove efixes
    note:
        exit_json if an exception raises
        Create and build
            results['meta']['0.report']
            results['meta']['1.parse']
    return:
        True if flrtvc succeeded
        False otherwise
    """
    global workdir

    if force:
        remove_efix()

    results['meta']['0.report'] = []

    # Run 'lslpp -Lcq' on the system and save to file
    lslpp_file = os.path.join(workdir, 'lslpp.txt')
    if os.path.exists(lslpp_file):
        os.remove(lslpp_file)
    run_lslpp(lslpp_file)

    # Run 'emgr -lv3' on the system and save to file
    emgr_file = os.path.join(workdir, 'emgr.txt')
    if os.path.exists(emgr_file):
        os.remove(emgr_file)
    run_emgr(emgr_file)

    # Wait until threads finish
    wait_all()

    if not os.path.exists(lslpp_file) or not os.path.exists(emgr_file):
        if not os.path.exists(lslpp_file):
            results['meta']['message'].append('Failed to list filsets (lslpp), {} does not exist'
                                              .format(lslpp_file))
        if not os.path.exists(emgr_file):
            results['meta']['message'].append('Failed to list fixes (emgr), {} does not exist'
                                              .format(emgr_file))
        return False

    # Prepare flrtvc command
    cmd = [flrtvc_path, '-e', emgr_file, '-l', lslpp_file]
    if params['apar_type'] and params['apar_type'] != 'all':
        cmd += ['-t', params['apar_type']]
    if params['apar_csv']:
        cmd += ['-f', params['apar_csv']]
    if params['filesets']:
        cmd += ['-g', params['filesets']]

    # Run flrtvc in compact mode
    logging.debug('run flrtvc in compact mode: cmd="{}"'.format(' '.join(cmd)))
    rc, stdout, stderr = module.run_command(cmd)
    if rc != 0 and rc != 2:
        msg = 'Failed to get flrtvc report, rc={}'.format(rc)
        logging.error(msg)
        logging.error('cmd:{} failed rc={}'.format(cmd, rc))
        logging.error('stdout:{}'.format(stdout))
        logging.error('stderr:{}'.format(stderr))
        results['meta']['messages'].append(msg + " stderr: {}".format(stderr))
        results['meta']['0.report'].append(msg)
        return False

    results['meta'].update({'0.report': stdout.splitlines()})

    # Save to file
    if params['dst_path']:
        filename = os.path.join(params['dst_path'], 'flrtvc.txt')
        with open(filename, 'w') as myfile:
            if params['verbose']:
                cmd += ['-v']

            logging.debug('write flrtvc report to file, cmd "{}"'.format(' '.join(cmd)))
            rc, stdout, stderr = module.run_command(cmd)
            # quick fix as flrtvc.ksh returns 2 if vulnerabities with some fixes found
            if rc != 0 and rc != 2:
                msg = 'Failed to save flrtvc report in file, rc={}'.format(rc)
                logging.error(msg)
                logging.error('cmd:{} failed rc={}'.format(cmd, rc))
                logging.error('stdout:{}'.format(stdout))
                logging.error('stderr:{}'.format(stderr))
                results['meta']['messages'].append(msg)
            myfile.write(stdout)

    return True


@logged
def run_parser(report):
    """
    Parse report by extracting URLs
    args:
        report  (str): The compact report
    note:
        Create and build results['meta']['1.parse']
    """
    dict_rows = csv.DictReader(report, delimiter='|')
    pattern = re.compile(r'^(http|https|ftp)://(aix.software.ibm.com|public.dhe.ibm.com)'
                         r'/(aix/ifixes/.*?/|aix/efixes/security/.*?.tar)$')
    rows = []
    for row in dict_rows:
        rows.append(row['Download URL'])
    selected_rows = [row for row in rows if pattern.match(row) is not None]

    rows = list(set(selected_rows))  # remove duplicates
    logging.debug('extracted {} urls in the report'.format(len(rows)))
    results['meta'].update({'1.parse': rows})


@logged
def run_downloader(urls, dst_path, resize_fs=True):
    """
    Download URLs and check efixes
    args:
        urls      (list): The list of URLs to download
        dst_path   (str): Path directory where to download
        resize_fs (bool): Increase the filesystem size if needed
    note:
        Create and build
            results['meta']['2.discover']
            results['meta']['3.download']
            results['meta']['4.1.reject']
            results['meta']['4.2.check']
    """
    out = {'messages': results['meta']['messages'],
           '2.discover': [],
           '3.download': [],
           '4.1.reject': [],
           '4.2.check': []}

    for url in urls:
        protocol, srv, rep, name = re.search(r'^(.*?)://(.*?)/(.*)/(.*)$', url).groups()
        logging.debug('protocol={}, srv={}, rep={}, name={}'
                      .format(protocol, srv, rep, name))

        if '.epkg.Z' in name:  # URL as an efix file
            logging.debug('treat url as an epkg file')
            out['2.discover'].extend(name)

            # download epkg file
            epkg = os.path.abspath(os.path.join(dst_path, name))
            if download(url, epkg, resize_fs):
                out['3.download'].append(epkg)

        elif '.tar' in name:  # URL as a tar file
            logging.debug('treat url as a tar file')
            dst = os.path.abspath(os.path.join(dst_path, name))

            # download and open tar file
            if download(url, dst, resize_fs):
                tar = tarfile.open(dst, 'r')

                # find all epkg in tar file
                epkgs = [epkg for epkg in tar.getnames() if re.search(r'(\b[\w.-]+.epkg.Z\b)$', epkg)]
                out['2.discover'].extend(epkgs)
                logging.debug('found {} epkg.Z file in tar file'.format(len(epkgs)))

                # extract epkg
                tar_dir = os.path.join(dst_path, 'tardir')
                if not os.path.exists(tar_dir):
                    os.makedirs(tar_dir)
                for epkg in epkgs:
                    try:
                        tar.extract(epkg, tar_dir)
                    except (OSError, IOError, tarfile.TarError) as exc:
                        if resize_fs and increase_fs(tar_dir):
                            try:
                                tar.extract(epkg, tar_dir)
                            except (OSError, IOError, tarfile.TarError) as exc:
                                msg = 'Cannot extract tar file {}'.format(epkg)
                                logging.error(msg)
                                logging.error('EXCEPTION {}'.format(exc))
                                results['meta']['messages'].append(msg)
                                continue
                        else:
                            msg = 'Cannot extract tar file {}'.format(epkg)
                            logging.error(msg)
                            logging.error('EXCEPTION {}'.format(exc))
                            results['meta']['messages'].append(msg)
                            continue
                    out['3.download'].append(os.path.abspath(os.path.join(tar_dir, epkg)))

        else:  # URL as a Directory
            logging.debug('treat url as a directory')
            # pylint: disable=protected-access
            response = urllib.urlopen(url, context=ssl._create_unverified_context())

            # find all epkg in html body
            epkgs = [epkg for epkg in re.findall(r'(\b[\w.-]+.epkg.Z\b)', response.read())]

            epkgs = list(set(epkgs))

            out['2.discover'].extend(epkgs)
            logging.debug('found {} epkg.Z file in html body'.format(len(epkgs)))

            # download epkg
            epkgs = [os.path.abspath(os.path.join(dst_path, epkg)) for epkg in epkgs
                     if download(os.path.join(url, epkg),
                                 os.path.abspath(os.path.join(dst_path, epkg)),
                                 resize_fs)]
            out['3.download'].extend(epkgs)

    # Get installed filesets' levels
    lpps_lvl = parse_lpps_info()

    # Build the dict of current fileset with their level
    curr_efixes = parse_emgr()

    # check prerequisite
    (out['4.2.check'], out['4.1.reject']) = check_epkgs(out['3.download'],
                                                        lpps_lvl, curr_efixes)
    results['meta'].update(out)


@logged
def run_installer(epkgs, dst_path, resize_fs=True):
    """
    Install epkgs efixes
    args:
        epkgs     (list): The list of efixes to install
        dst_path   (str): Path directory where to install
        resize_fs (bool): Increase the filesystem size if needed
    return:
        True if geninstall succeeded
        False otherwise
    note:
        epkgs should be results['meta']['4.2.check'] which is
        sorted against packaging date. Do not change the order.
        Create and build results['meta']['5.install']
    """
    if not epkgs:
        return True

    destpath = os.path.abspath(os.path.join(dst_path))
    destpath = os.path.join(destpath, 'flrtvc_lpp_source', 'emgr', 'ppc')
    # create lpp source location
    if not os.path.exists(destpath):
        os.makedirs(destpath)

    # copy efix destpath lpp source
    epkgs_base = []
    for epkg in epkgs:
        try:
            shutil.copy(epkg, destpath)
        except (IOError, shutil.Error) as exc:
            if resize_fs and increase_fs(destpath):
                try:
                    shutil.copy(epkg, destpath)
                except (IOError, shutil.Error) as exc:
                    msg = 'Cannot copy file {} to {}'.format(epkg, destpath)
                    logging.error(msg)
                    logging.error('EXCEPTION {}'.format(exc))
                    results['meta']['messages'].append(msg)
                    continue
            else:
                msg = 'Cannot copy file {} to {}'.format(epkg, destpath)
                logging.error(msg)
                logging.error('EXCEPTION {}'.format(exc))
                results['meta']['messages'].append(msg)
                continue
        epkgs_base.append(os.path.basename(epkg))

    # return error if we have nothing to install
    if not epkgs_base:
        return False

    efixes = ' '.join(epkgs_base)

    # perform customization
    cmd = ['/usr/sbin/geninstall', '-d', destpath, efixes]
    logging.debug('Perform customization, cmd "{}"'.format(' '.join(cmd)))
    rc, stdout, stderr = module.run_command(cmd)
    logging.debug('geninstall stdout:{}'.format(stdout))

    results['changed'] = True
    results['meta'].update({'5.install': stdout.splitlines()})

    if rc != 0:
        msg = 'Cannot perform customization, rc={}'.format(rc)
        logging.error(msg)
        logging.error('cmd={} rc={} stdout:{} stderr:{}'
                      .format(cmd, rc, stdout, stderr))
        results['meta']['messages'].append(msg)
        return False

    return True


@wait_threaded(THRDS)
def wait_all():
    """
    Do nothing
    """
    pass


def increase_fs(dest):
    """
    Increase filesystem by 100Mb
    args:
        dst (str): The absolute filename
    return:
        True if increase succeeded
        False otherwise
    """
    cmd = ['/bin/df', '-c', dest]
    rc, stdout, stderr = module.run_command(cmd)
    if rc == 0:
        mount_point = stdout.splitlines()[1].split(':')[6]
        cmd = ['chfs', '-a', 'size=+100M', mount_point]
        rc, stdout, stderr = module.run_command(cmd)
        if rc == 0:
            logging.debug('{}: increased 100Mb: {}'.format(mount_point, stdout))
            return True

    logging.warning('{}: cmd:{} failed rc={} stdout:{} stderr:{}'
                    .format(mount_point, cmd, rc, stdout, stderr))
    msg = 'Cannot increase filesystem for {}.'.format(dest)
    results['meta']['messages'].append(msg)
    return False


###################################################################################################

def main():
    global module
    global results
    global workdir

    module = AnsibleModule(
        argument_spec=dict(
            apar=dict(required=False, choices=['sec', 'hiper', 'all', None], default=None),
            filesets=dict(required=False, type='str'),
            csv=dict(required=False, type='str'),
            path=dict(required=False, type='str', default='/var/adm/ansible/work'),
            verbose=dict(required=False, type='bool', default=False),
            force=dict(required=False, type='bool', default=False),
            clean=dict(required=False, type='bool', default=False),
            check_only=dict(required=False, type='bool', default=False),
            download_only=dict(required=False, type='bool', default=False),
            increase_fs=dict(required=False, type='bool', default=True),
        ),
        supports_check_mode=True
    )

    results = dict(
        changed=False,
        msg='',
        meta={'messages': []}
        # meta structure will be updated as follow:
        # meta={'messages': [],     detail execution messages
        #       '0.report': [],     run_flrtvc reports the vulnerabilities
        #       '1.parse': [],      run_parser builds the list of URLs
        #       '2.discover': [],   run_downloader builds the list of epkgs found in URLs
        #       '3.download': [],   run_downloader builds the list of downloaded epkgs
        #       '4.1.reject': [],   check_epkgs builds the list of rejected epkgs
        #       '4.2.check': [],    check_epkgs builds the list of epkgs checking prerequisites
        #       '5.install': []}    run_installer builds the list of installed epkgs
    )

    # Open log file
    logdir = os.path.abspath(os.path.join('var', 'adm', 'ansible'))
    logpath = os.path.join(logdir, 'flrtvc_debug.log')
    if not os.path.exists(logdir):
        os.makedirs(logdir, mode=0o744)
    logging.basicConfig(filename=logpath,
                        format='[%(asctime)s] %(levelname)s: [%(funcName)s:%(thread)d] %(message)s',
                        level=logging.DEBUG)

    logging.debug('*** START ***')
    module.run_command_environ_update = dict(LANG='C', LC_ALL='C', LC_MESSAGES='C', LC_CTYPE='C')

    # ===========================================
    # Get module params
    # ===========================================
    logging.debug('*** INIT ***')

    # Used for independence vs Ansible options
    flrtvc_params = {'apar_type': module.params['apar'],
                     'apar_csv': module.params['csv'],
                     'filesets': module.params['filesets'],
                     'dst_path': module.params['path'],
                     'verbose': module.params['verbose']}
    force = module.params['force']
    clean = module.params['clean']
    check_only = module.params['check_only']
    download_only = module.params['download_only']
    resize_fs = module.params['increase_fs']

    # Create working directory if needed
    workdir = os.path.abspath(os.path.join(flrtvc_params['dst_path'], 'work'))
    if not os.path.exists(workdir):
        os.makedirs(workdir, mode=0o744)

    # ===========================================
    # Install flrtvc script
    # ===========================================
    logging.debug('*** INSTALL ***')
    flrtvc_dir = os.path.abspath(os.path.join('usr', 'bin'))
    flrtvc_path = os.path.abspath(os.path.join(flrtvc_dir, 'flrtvc.ksh'))

    if os.path.exists(flrtvc_path):
        try:
            os.remove(flrtvc_path)
        except OSError as exc:
            msg = 'Exception removing {}, exception={}'.format(flrtvc_path, exc)
            logging.warning(msg)
            results['meta']['messages'].append(msg)

    flrtvc_dst = os.path.abspath(os.path.join(workdir, 'FLRTVC-latest.zip'))
    if not download('https://www-304.ibm.com/webapp/set2/sas/f/flrt3/FLRTVC-latest.zip',
                    flrtvc_dst, resize_fs):
        if clean and os.path.exists(workdir):
            shutil.rmtree(workdir, ignore_errors=True)
        results['msg'] = 'Failed to download FLRTVC-latest.zip'
        module.fail_json(**results)

    if not unzip(flrtvc_dst, flrtvc_dir, resize_fs):
        if clean and os.path.exists(workdir):
            shutil.rmtree(workdir, ignore_errors=True)
        results['msg'] = 'Failed to unzip FLRTVC-latest.zip'
        module.fail_json(**results)

    flrtvc_stat = os.stat(flrtvc_path)
    if not flrtvc_stat.st_mode & stat.S_IEXEC:
        os.chmod(flrtvc_path, flrtvc_stat.st_mode | stat.S_IEXEC)

    # ===========================================
    # Run flrtvc script
    # ===========================================
    logging.debug('*** REPORT ***')
    if not run_flrtvc(flrtvc_path, flrtvc_params, force):
        msg = 'Failed to get vulnerabilities report, system will not be updated'
        results['msg'] = msg
        if clean and os.path.exists(workdir):
            shutil.rmtree(workdir, ignore_errors=True)
        module.fail_json(**results)

    if check_only:
        if clean and os.path.exists(workdir):
            shutil.rmtree(workdir, ignore_errors=True)
        results['msg'] = 'exit on check only'
        module.exit_json(**results)

    # ===========================================
    # Parse flrtvc report
    # ===========================================
    logging.debug('*** PARSE ***')
    run_parser(results['meta']['0.report'])

    # ===========================================
    # Download and check efixes
    # ===========================================
    logging.debug('*** DOWNLOAD ***')
    run_downloader(results['meta']['1.parse'], flrtvc_params['dst_path'], resize_fs)

    if download_only:
        if clean and os.path.exists(workdir):
            shutil.rmtree(workdir, ignore_errors=True)
        results['msg'] = 'exit on download only'
        module.exit_json(**results)

    # ===========================================
    # Install efixes
    # ===========================================
    logging.debug('*** UPDATE ***')
    if not run_installer(results['meta']['4.2.check'], flrtvc_params['dst_path'], resize_fs):
        msg = 'Failed to install fixes, please check meta and log data.'
        results['msg'] = msg
        if clean and os.path.exists(workdir):
            shutil.rmtree(workdir, ignore_errors=True)
        module.fail_json(**results)

    if clean and os.path.exists(workdir):
        shutil.rmtree(workdir, ignore_errors=True)

    results['msg'] = 'FLRTVC completed successfully'
    logging.info(results['msg'])
    module.exit_json(**results)


if __name__ == '__main__':
    main()
