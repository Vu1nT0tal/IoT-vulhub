#!/usr/bin/env python3

"""
Module that performs extraction. For usage, refer to documentation for the class
'Extractor'. This module can also be executed directly,
e.g. 'extractor.py <input> <output>'.
"""

import argparse
import hashlib
import multiprocessing
import os
import shutil
import tempfile
import traceback
import pathlib

import magic
import binwalk

class Extractor(object):
    """
    Class that extracts kernels and filesystems from firmware images, given an input file or directory and output directory.
    """

    # Directories that define the root of a UNIX filesystem, and the appropriate threshold condition
    UNIX_DIRS = ["bin", "etc", "dev", "home", "lib", "mnt", "opt", "root", "run", "sbin", "tmp", "usr", "var"]
    UNIX_THRESHOLD = 4

    # Lock to prevent concurrent access to visited set. Unfortunately, must be static because it cannot be pickled or passed as instance attribute.
    visited_lock = multiprocessing.Lock()

    def __init__(self, indir, outdir=None, rootfs=True, kernel=True):
        # Input firmware update file or directory
        self._input = os.path.abspath(indir)
        # Output firmware directory
        self.output_dir = os.path.abspath(outdir) if outdir else None

        # Whether to attempt to extract kernel
        self.do_kernel = kernel
        self.kernel_done = False

        # Whether to attempt to extract root filesystem
        self.do_rootfs = rootfs
        self.rootfs_done = False

        # Set containing MD5 checksums of visited items
        self.visited = dict()

        # List containing tagged items to extract as 2-tuple: (tag [e.g. MD5], path)
        self._list = list()

    def __getstate__(self):
        """
        Eliminate attributes that should not be pickled.
        """
        self_dict = self.__dict__.copy()
        del self_dict["_list"]
        return self_dict

    @staticmethod
    def io_dd(indir, offset, size, outdir):
        """
        Given a path to a target file, extract size bytes from specified offset to given output file.
        """
        if not size:
            return

        with open(indir, "rb") as ifp:
            with open(outdir, "wb") as ofp:
                ifp.seek(offset, 0)
                ofp.write(ifp.read(size))

    @staticmethod
    def magic(indata, mime=False):
        """
        Performs file magic while maintaining compatibility with different libraries.
        """

        try:
            if mime:
                mymagic = magic.open(magic.MAGIC_MIME_TYPE)
            else:
                mymagic = magic.open(magic.MAGIC_NONE)
            mymagic.load()
        except AttributeError:
            mymagic = magic.Magic(mime)
            mymagic.file = mymagic.from_file

        try:
            return mymagic.file(indata)
        except magic.MagicException:
            return None

    @staticmethod
    def io_md5(target):
        """
        Performs MD5 with a block size of 64kb.
        """
        blocksize = 65536
        hasher = hashlib.md5()

        with open(target, 'rb') as ifp:
            buf = ifp.read(blocksize)
            while buf:
                hasher.update(buf)
                buf = ifp.read(blocksize)
            return hasher.hexdigest()

    @staticmethod
    def io_rm(target):
        """
        Attempts to recursively delete a directory.
        """
        shutil.rmtree(target, ignore_errors=True, onerror=Extractor._io_err)

    @staticmethod
    def _io_err(function, path, excinfo):
        """
        Internal function used by '_rm' to print out errors.
        """
        print(("!! %s: Cannot delete %s!\n%s" % (function, path, excinfo)))

    @staticmethod
    def io_find_rootfs(start, recurse=True):
        """
        Attempts to find a Linux root directory.
        """

        # Recurse into single directory chains, e.g. jffs2-root/fs_1/.../
        path = start
        while (len(os.listdir(path)) == 1 and
               os.path.isdir(os.path.join(path, os.listdir(path)[0]))):
            path = os.path.join(path, os.listdir(path)[0])

        # count number of unix-like directories
        count = 0
        for subdir in os.listdir(path):
            if subdir in Extractor.UNIX_DIRS and \
                os.path.isdir(os.path.join(path, subdir)) and \
                    len(os.listdir(os.path.join(path, subdir))) > 0:
                count += 1

        # check for extracted filesystem, otherwise update queue
        if count >= Extractor.UNIX_THRESHOLD:
            return (True, path)

        # in some cases, multiple filesystems may be extracted, so recurse to find best one
        if recurse:
            for subdir in os.listdir(path):
                if os.path.isdir(os.path.join(path, subdir)):
                    res = Extractor.io_find_rootfs(os.path.join(path, subdir), False)
                    if res[0]:
                        return res

        return (False, start)

    def extract(self):
        """
        Perform extraction of firmware updates from input to tarballs in output directory.
        """
        if os.path.isdir(self._input):
            for path, _, files in os.walk(self._input):
                for item in files:
                    self._list.append(os.path.join(path, item))
        elif os.path.isfile(self._input):
            self._list.append(self._input)

        if self.output_dir and not os.path.isdir(self.output_dir):
            os.makedirs(self.output_dir)

        for item in self._list:
            self._extract_item(item)

    def _extract_item(self, path):
        """
        Wrapper function that creates an ExtractionItem and calls the extract() method.
        """

        ExtractionItem(self, path, 0).extract()

class ExtractionItem(object):
    """
    Class that encapsulates the state of a single item that is being extracted.
    """

    # Maximum recursion breadth and depth
    RECURSION_BREADTH = 10
    RECURSION_DEPTH = 3

    def __init__(self, extractor, path, depth):
        # Temporary directory
        self.temp = None

        # Recursion depth counter
        self.depth = depth

        # Reference to parent extractor object
        self.extractor = extractor

        # File path
        self.item = path

        # Checksum
        self.checksum = Extractor.io_md5(path)

        # Tag
        self.tag = "1"

        # Output file path and filename prefix
        self.output = os.path.join(self.extractor.output_dir, self.tag) if \
                                   self.extractor.output_dir else None

        # Status, with terminate indicating early termination for this item
        self.terminate = False
        self.status = None
        self.update_status()

    def __del__(self):
        if self.temp:
            self.printf(">> Cleaning up %s..." % self.temp)
            Extractor.io_rm(self.temp)

    def printf(self, fmt):
        """
        Prints output string with appropriate depth indentation.
        """
        print(("\t" * self.depth + fmt))

    def get_kernel_status(self):
        """
        Get the flag corresponding to the kernel status.
        """
        return self.extractor.kernel_done

    def get_rootfs_status(self):
        """
        Get the flag corresponding to the root filesystem status.
        """
        return self.extractor.rootfs_done

    def update_status(self):
        """
        Updates the status flags using the tag to determine completion status.
        """
        kernel_done = os.path.isfile(self.get_kernel_path()) \
            if self.extractor.do_kernel and self.output \
            else not self.extractor.do_kernel

        rootfs_done = os.path.isfile(self.get_rootfs_path()) \
            if self.extractor.do_rootfs and self.output \
            else not self.extractor.do_rootfs

        self.status = (kernel_done, rootfs_done)
        self.extractor.kernel_done = kernel_done
        self.extractor.rootfs_done = rootfs_done

        return self.get_status()

    def get_status(self):
        """
        Returns True if early terminate signaled, extraction is complete, otherwise False.
        """
        return True if self.terminate or all(i for i in self.status) else False

    def get_kernel_path(self):
        """
        Return the full path (including filename) to the output kernel file.
        """
        return self.output + ".kernel" if self.output else None

    def get_rootfs_path(self):
        """
        Return the full path (including filename) to the output root filesystem file.
        """
        return self.output + ".tar.gz" if self.output else None

    def extract(self):
        """
        Perform the actual extraction of firmware updates, recursively. Returns
        True if extraction complete, otherwise False.
        """
        self.printf("\n" + self.item.encode("utf-8", "replace").decode("utf-8"))

        # check if item is complete
        if self.get_status():
            self.printf(">> Skipping: completed!")
            return True

        # check if exceeding recursion depth
        if self.depth > ExtractionItem.RECURSION_DEPTH:
            self.printf(">> Skipping: recursion depth %d" % self.depth)
            return self.get_status()

        # check if checksum is in visited set
        self.printf(">> MD5: %s" % self.checksum)
        with Extractor.visited_lock:
            # Skip the same checksum only in the same status
            # asus_latest(FW_RT_N12VP_30043804057.zip) firmware
            if (self.checksum in self.extractor.visited and
                    self.extractor.visited[self.checksum] == self.status):
                self.printf(">> Skipping: %s..." % self.checksum)
                return self.get_status()
            else:
                self.extractor.visited[self.checksum] = self.status

        # check if filetype is blacklisted
        if self._check_blacklist():
            return self.get_status()

        # create working directory
        self.temp = tempfile.mkdtemp()

        # Move to temporary directory so binwalk does not write to input
        os.chdir(self.temp)

        try:
            self.printf(">> Tag: %s" % self.tag)
            self.printf(">> Temp: %s" % self.temp)
            self.printf(">> Status: Kernel: %s, Rootfs: %s, Do_Kernel: %s, \
                Do_Rootfs: %s" % (self.get_kernel_status(),
                                  self.get_rootfs_status(),
                                  self.extractor.do_kernel,
                                  self.extractor.do_rootfs))

            for module in binwalk.scan(self.item, "-e", "-r", "-C", self.temp,
                                       signature=True, quiet=True):
                prev_entry = None
                for entry in module.results:
                    desc = entry.description
                    dir_name = module.extractor.directory

                    if prev_entry and prev_entry.description == desc and \
                            'Zlib comparessed data' in desc:
                        continue
                    prev_entry = entry

                    self.printf('========== Depth: %d ===============' % self.depth)
                    self.printf("Name: %s" % self.item)
                    self.printf("Desc: %s" % desc)
                    self.printf("Directory: %s" % dir_name)

                    self._check_firmware(module, entry)

                    if not self.get_rootfs_status():
                        self._check_rootfs(module, entry)

                    if not self.get_kernel_status():
                        self._check_kernel(module, entry)

                    if self.update_status():
                        self.printf(">> Skipping: completed!")
                        return True
                    else:
                        self._check_recursive(module, entry)

        except Exception:
            print ("ERROR: ", self.item)
            traceback.print_exc()

        return False

    def _check_blacklist(self):
        """
        Check if this file is blacklisted for analysis based on file type.
        """
        real_path = os.path.realpath(self.item)

        # First, use MIME-type to exclude large categories of files
        filetype = Extractor.magic(real_path.encode("utf-8", "surrogateescape"), mime=True)
        if filetype:
            if any(s in filetype for s in ["application/x-executable",
                                           "application/x-dosexec",
                                           "application/x-object",
                                           "application/x-sharedlib",
                                           "application/pdf",
                                           "application/msword",
                                           "image/", "text/", "video/"]):
                self.printf(">> Skipping: %s..." % filetype)
                return True

        # Next, check for specific file types that have MIME-type 'application/octet-stream'
        filetype = Extractor.magic(real_path.encode("utf-8", "surrogateescape"))
        if filetype:
            if any(s in filetype for s in ["executable", "universal binary",
                                           "relocatable", "bytecode", "applet", "shared"]):
                self.printf(">> Skipping: %s..." % filetype)
                return True

        # Finally, check for specific file extensions that would be incorrectly identified
        black_lists = ['.dmg', '.so', '.so.0']
        for black in black_lists:
            if self.item.endswith(black):
                self.printf(">> Skipping: %s..." % (self.item))
                return True

        return False

    def _check_firmware(self, module, entry):
        """
        If this file is of a known firmware type, directly attempt to extract the kernel and root filesystem.
        """
        dir_name = module.extractor.directory
        desc = entry.description
        if 'header' in desc:
            # uImage
            if "uImage header" in desc:
                if not self.get_kernel_status() and "OS Kernel Image" in desc:
                    kernel_offset = entry.offset + 64
                    kernel_size = 0

                    for stmt in desc.split(','):
                        if "image size:" in stmt:
                            kernel_size = int(''.join(
                                i for i in stmt if i.isdigit()), 10)

                    if kernel_size != 0 and kernel_offset + kernel_size \
                        <= os.path.getsize(self.item):
                        self.printf(">>>> %s" % desc)

                        tmp_fd, tmp_path = tempfile.mkstemp(dir=self.temp)
                        os.close(tmp_fd)
                        Extractor.io_dd(self.item, kernel_offset,
                                        kernel_size, tmp_path)
                        kernel = ExtractionItem(self.extractor, tmp_path, self.depth)
                        return kernel.extract()

            # TP-Link or TRX
            elif not self.get_kernel_status() and \
                not self.get_rootfs_status() and \
                "rootfs offset: " in desc and "kernel offset: " in desc:
                image_size = os.path.getsize(self.item)
                header_size = 0
                kernel_offset = 0
                kernel_size = 0
                rootfs_offset = 0
                rootfs_size = 0

                for stmt in desc.split(','):
                    if "header size" in stmt:
                        header_size = int(stmt.split(':')[1].split()[0])
                    elif "kernel offset:" in stmt:
                        kernel_offset = int(stmt.split(':')[1], 16)
                    elif "kernel length:" in stmt:
                        kernel_size = int(stmt.split(':')[1], 16)
                    elif "rootfs offset:" in stmt:
                        rootfs_offset = int(stmt.split(':')[1], 16)
                    elif "rootfs length:" in stmt:
                        rootfs_size = int(stmt.split(':')[1], 16)

                # add entry offset
                kernel_offset += entry.offset
                rootfs_offset += entry.offset + header_size

                # compute sizes if only offsets provided
                if rootfs_offset < kernel_offset:
                    if rootfs_size == 0:
                        rootfs_size = kernel_offset - rootfs_offset
                    if kernel_size == 0:
                        kernel_size = image_size - kernel_offset
                elif rootfs_offset > kernel_offset:
                    if kernel_size == 0:
                        kernel_size = rootfs_offset - kernel_offset
                    if rootfs_size == 0:
                        rootfs_size = image_size - rootfs_offset

                self.printf('image size: %d' % image_size)
                self.printf('rootfs offset: %d' % rootfs_offset)
                self.printf('rootfs size: %d' % rootfs_size)
                self.printf('kernel offset: %d' % kernel_offset)
                self.printf('kernel size: %d' % kernel_size)

                # ensure that computed values are sensible
                if kernel_size > 0 and rootfs_size > 0 and \
                        kernel_offset + kernel_size <= image_size and \
                        rootfs_offset + rootfs_size <= image_size:
                    self.printf(">>>> %s" % desc)

                    tmp_fd, tmp_path = tempfile.mkstemp(dir=self.temp)
                    os.close(tmp_fd)
                    Extractor.io_dd(self.item, kernel_offset, kernel_size,
                                    tmp_path)
                    kernel = ExtractionItem(self.extractor, tmp_path, self.depth)
                    kernel.extract()

                    tmp_fd, tmp_path = tempfile.mkstemp(dir=self.temp)
                    os.close(tmp_fd)
                    Extractor.io_dd(self.item, rootfs_offset, rootfs_size,
                                    tmp_path)
                    rootfs = ExtractionItem(self.extractor, tmp_path, self.depth)
                    rootfs.extract()
                    return True
        return False

    def _check_kernel(self, module, entry):
        """
        If this file contains a kernel version string, assume it is a kernel.
        """
        dir_name = module.extractor.directory
        desc = entry.description
        if 'kernel' in desc:
            if self.get_kernel_status(): return True
            else:
                if "kernel version" in desc:
                    if "Linux" in desc:
                        if self.get_kernel_path():
                            shutil.copy(self.item, self.get_kernel_path())
                        else:
                            self.extractor.do_kernel = False
                        self.printf(">>>> %s" % desc)
                        return True
                    # VxWorks, etc
                    else:
                        self.printf(">>>> Ignoring: %s" % desc)
        return False

    def _check_rootfs(self, module, entry):
        """
        If this file contains a known filesystem type, extract it.
        """
        dir_name = module.extractor.directory
        desc = entry.description
        if 'filesystem' in desc or 'archive' in desc or 'compressed' in desc:
            if self.get_rootfs_status(): return True
            else:
                if dir_name:
                    unix = Extractor.io_find_rootfs(dir_name)
                    if not unix[0]:
                        self.printf(">>>> Extraction failed!")
                        return False

                    self.printf(">>>> Found Linux filesystem in %s!" % unix[1])
                    if self.output:
                        shutil.make_archive(self.output, "gztar",
                                            root_dir=unix[1])
                    else:
                        self.extractor.do_rootfs = False
                    return True
        return False

    # treat both archived and compressed files using the same pathway. this is
    # because certain files may appear as e.g. "xz compressed data" but still
    # extract into a root filesystem.
    def _check_recursive(self, module, entry):
        """
        Unified implementation for checking both "archive" and "compressed" items.
        """
        dir_name = module.extractor.directory
        desc = entry.description
        # filesystem for the netgear WNR2000 firmware (kernel in Squashfs)
        if 'filesystem' in desc or 'archive' in desc or 'compressed' in desc:
            if dir_name:
                self.printf(">> Recursing into %s ..." % desc)
                count = 0
                for root, _, files in os.walk(dir_name):
                    # sort both descending alphabetical and increasing length
                    files.sort()
                    files.sort(key=len)

                    # handle case where original file name is restored; put it to front of queue
                    if desc and "original file name:" in desc:
                        orig = None
                        for stmt in desc.split(","):
                            if "original file name:" in stmt:
                                orig = stmt.split("\"")[1]
                        if orig and orig in files:
                            files.remove(orig)
                            files.insert(0, orig)

                    for filename in files:
                        path = os.path.join(root, filename)
                        if not pathlib.Path(path).is_file():
                            continue
                        new_item = ExtractionItem(self.extractor, path, self.depth+1)
                        if new_item.extract():
                            if self.update_status():
                                return True
                        count += 1
        return False

def main():
    parser = argparse.ArgumentParser(description="Extracts filesystem and kernel from Linux-based firmware images")
    parser.add_argument("input", action="store", help="Input file or directory")
    parser.add_argument("output", action="store", nargs="?", default="images", help="Output directory for extracted firmware")
    parser.add_argument("-nf", dest="rootfs", action="store_false", default=True, help="Disable extraction of root filesystem")
    parser.add_argument("-nk", dest="kernel", action="store_false", default=True, help="Disable extraction of kernel")
    result = parser.parse_args()

    extract = Extractor(result.input, result.output, result.rootfs, result.kernel)
    extract.extract()

if __name__ == "__main__":
    main()
