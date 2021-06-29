#!/usr/bin/env python3
'''Fast debian package creator'''

import argparse
import os
import sys
import shutil
import tempfile
import logging

import pigz_python


def createDebianPackage(args):
    '''
    Create a .deb file like dpkg-deb
    A debian package is a simple ar archive with 3 files.
    https://en.wikipedia.org/wiki/Deb_(file_format)

    $ file foo.deb 
    foo.deb: Debian binary package (format 2.0), with control.tar.gz, data compression gz

    $ ar -t foo.deb 
    debian-binary
    control.tar.gz
    data.tar.gz

    $ ar x foo.deb 
    $ ls
    control.tar.gz			data.tar.gz			debian-binary			foo.deb
    sandbox$ tar tf data.tar.gz 
    ./usr/local/
    ./usr/local/bin/
    ./usr/local/bin/fake_server
    ./usr/local/bin/fake_server.sh

    $ tar tf control.tar.gz 
    ./
    ./control
    ./postinst

    $ cat debian-binary 
    2.0
    '''
    # Make input paths absolute
    root = os.path.abspath(args.build)
    deb = os.path.abspath(args.deb)
    if os.path.exists(deb):
        os.unlink(deb)

    pwd = os.getcwd()
    tmpDir = tempfile.mkdtemp()
    os.chdir(tmpDir)

    # 1. Create compressed tarball for control data
    controlRoot = os.path.join(root, 'DEBIAN')
    archive = shutil.make_archive(base_name='control',
                                  format='gztar',
                                  root_dir=controlRoot)
    shutil.rmtree(controlRoot)

    # 2. Create tarball for binary data
    logging.info('Creating data archive')
    archive = shutil.make_archive(base_name='data',
                                  format='tar',
                                  root_dir=root)

    # Compress the .tar file ourself with pigz which is faster
    # than the gzip binary
    logging.info(f'Compressing data at zlib compression level {args.compress_level}')
    pigz_python.compress_file(archive, compresslevel=args.compress_level)
    os.unlink(archive)

    # 3. Create debian file
    with open('debian-binary', 'w') as f:
        f.write('2.0\n')

    # Finally create the ar archive, aka the debian package
    logging.info('Creating ar archive')
    os.system(f'ar r {deb} debian-binary control.tar.gz data.tar.gz')

    # Cleanup temp dir
    os.chdir(pwd)
    shutil.rmtree(tmpDir)


if __name__ == "__main__":
    logging.getLogger().setLevel(logging.INFO)
    logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s')

    parser = argparse.ArgumentParser()
    parser.add_argument("--build", help="Input folder", required=True)
    parser.add_argument("--deb", help="Output .deb file", required=True)
    parser.add_argument("--gzip_only", help="Compression level")
    parser.add_argument("--compress_level", help="Compression level", default=6, type=int)
    args = parser.parse_args()

    if args.gzip_only:
        # Test mode to see how fast we can gzip compress a file
        pigz_python.compress_file(args.gzip_only, compresslevel=args.compress_level)
    else:
        createDebianPackage(args)
