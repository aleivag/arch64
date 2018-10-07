#!/usr/bin/env python3

from pathlib import Path
from tempfile import TemporaryDirectory
from subprocess import check_call
from datetime import datetime

BOXES = Path('boxes')
IMG_VER = sorted(BOXES .iterdir() if BOXES .is_dir() else [], reverse=True)
if IMG_VER:
    IMG_VER = IMG_VER[0].absolute()

#IMG_VER = 'aleivag/arch64'

VAGRANT_FILE = f"""

Vagrant.configure("2") do |config|
  config.vm.box = "aleivag/arch64"

  config.vm.synced_folder ".", "/vagrant", disabled: true

  config.vm.provision "shell", path: "setup.sh"

end

"""

SETUP_SH = """#!/bin/bash

# set -e

rm -rf /home/terry/ /home/vagrant/neofetch

pacman -Syy
pacman --noconfirm -S cython ipython python-pip python-wheel vim git archlinux-keyring
pacman --noconfirm -Su
pacman --noconfirm -Sc

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

    def up(self):
        (self.base / 'Vagrantfile').write_text(self.vagrant_file)
        (self.base / 'setup.sh').write_text(self.setup_sh)
        check_call(['vagrant', 'up'], cwd=self.base)

    def destroy(self):
        check_call(['vagrant', 'destroy', '--force'], cwd=self.base)

    def package(self, pkg):
        check_call(['vagrant', 'package', '--output', pkg], cwd=self.base)

    def __enter__(self):
        #self.up()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.destroy()


with TemporaryDirectory() as tmpd, Vagrant(tmpd, VAGRANT_FILE, SETUP_SH) as vagrant:
    tmpd = Path(tmpd)
    print(tmpd)

    print("Creating Vagrantfile")
    print(VAGRANT_FILE)
    vagrant.up()
    vagrant.package(NEWPKG.absolute())


