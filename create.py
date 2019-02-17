#!/usr/bin/env python3

from pathlib import Path
from tempfile import TemporaryDirectory
from subprocess import check_call
from datetime import datetime

def repeat(cmd, r=4):
    return ' || '.join(cmd for _ in range(r))

BOXES = Path('boxes')
IMG_VER = sorted(BOXES .iterdir() if BOXES .is_dir() else [], reverse=True)
if IMG_VER:
    IMG_VER = IMG_VER[0].absolute()

IMG_VER = 'aleivag/arch64'

VAGRANT_FILE = f"""

Vagrant.configure("2") do |config|
  config.vm.box = "{IMG_VER}"
  config.vm.box_check_update = true

  config.vm.synced_folder ".", "/vagrant", disabled: true

  config.vm.provision "shell", path: "setup.sh"

end

"""


SETUP_SH = f"""#!/bin/bash

set -e
set -x
rm -rf /home/terry/

{repeat("pacman --noconfirm -Syy")}
{repeat("pacman --noconfirm -Sy archlinux-keyring")}
{repeat("pacman --noconfirm -Sy cython ipython python-pip python-wheel vim git")}
{repeat("pacman --noconfirm -Syu")}
{repeat("pacman --noconfirm -Sc")}

rm -f  /home/*/.bash_history /root/.bash_history
rm -rf  /var/log/* /var/cache/pacman/*


echo cleanup root
dd if=/dev/zero of=/EMPTY bs=1M || /bin/true
rm -f /EMPTY

"""

NEWPKG = Path('boxes') / f"arch64-{datetime.today().strftime('%Y.%m.%d')}.box"

class Vagrant:
    def __init__(self, base, vagrant_file, setup_sh):
        self.base = Path(base)
        self.vagrant_file = vagrant_file
        self.setup_sh = setup_sh

    def _vagrant_call(self, cmd, *args, **kwargs):
        check_call(['vagrant', cmd, *args], cwd=self.base, **kwargs)

    def ssh(self):
        self._vagrant_call('ssh')

    def up(self):
        (self.base / 'Vagrantfile').write_text(self.vagrant_file)
        (self.base / 'setup.sh').write_text(self.setup_sh)
        self._vagrant_call('up')


    def destroy(self):
        self._vagrant_call('destroy', '--force')

    def package(self, pkg):
        self._vagrant_call('package', '--output', pkg)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.destroy()


with TemporaryDirectory() as tmpd, Vagrant(tmpd, VAGRANT_FILE, SETUP_SH) as vagrant:
    tmpd = Path(tmpd)
    print(tmpd)

    print("Creating Vagrantfile")
    print(VAGRANT_FILE)
    vagrant.up()
    vagrant.ssh()
    vagrant.package(NEWPKG.absolute())


