#!/usr/bin/env python3

import os
import shutil
import tempfile
import collections
import platform
import unittest
import logging

from mk_deb import createDebianPackage


class TestDebCreation(unittest.TestCase):

    def setUp(self):
        self.pwd = os.path.dirname(os.path.realpath(__file__))
        self.tempDir = tempfile.mkdtemp()

    def tearDown(self):
        os.chdir(self.pwd)
        shutil.rmtree(self.tempDir)

    def testCreateAndInstall(self):
        '''
        Simple test using a reference input
        '''
        sandboxTarBall = os.path.join(self.pwd, 'mk_deb.test_data.tar')
        print(sandboxTarBall)

        # Copy the tarball and extract it
        shutil.copy(sandboxTarBall, self.tempDir)
        os.chdir(self.tempDir)
        os.system('tar xf mk_deb.test_data.tar')

        # Create the deb package
        Args = collections.namedtuple('Args', ['build', 'deb', 'compress_level', 'use_gzip_module'])
        createDebianPackage(Args('sandbox.ref', 'foo.deb', 8, False))

        # List the content of the archive
        with os.popen('ar t foo.deb') as f:
            output = f.read()

        referenceOutput = '''\
debian-binary
control.tar.gz
data.tar.gz
'''
        assert output == referenceOutput

        # Simple tests to extract members from the archive
        for filename in ['debian-binary', 'control.tar.gz', 'data.tar.gz']:
            assert os.system(f'ar x foo.deb {filename}') == 0
            assert os.system(f'cksum {filename}') == 0
            os.unlink(filename)

        if platform.system() == 'Linux':
            # Remove the package in case a previous install failed
            os.system('sudo dpkg -r mk_deb_fake_package')

            # Now try to install the debian package
            assert os.system('sudo dpkg -i foo.deb') == 0

            # Make sure that postinstall worked OK, and changed the installed file permission
            # to be owned by the www-data user 
            lsResult = os.popen("ls -lt /usr/local/bin/fake_server | awk '{ print $3 }'").read()
            assert lsResult == 'www-data' + '\n'

            # Try to run the installed binary, which just print hello. The binary was made as is
            #
            # $ cat /tmp/foo.c
            # #include <stdio.h>
            # 
            # int main () { puts("hello"); }
            # $ gcc -static /tmp/foo.c
            # $ ./a.out
            # hello
            # $ cp a.out sandbox.ref/usr/local/bin/fake_server
            # $ tar cf mk_deb.test_data.tar sandbox.ref
            #
            with os.popen("/usr/local/bin/fake_server.sh") as f:
                fakeServerResult = f.read()

            assert fakeServerResult == 'hello' + '\n'

            # Finally remove the .deb package
            assert os.system('sudo dpkg -r mk_deb_fake_package') == 0


if __name__ == "__main__":
    logging.getLogger().setLevel(logging.INFO)
    logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s')

    unittest.main()
