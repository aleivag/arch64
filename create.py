

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

rm -rf /home/terry/

pacman -Syy
pacman --noconfirm -S cython ipython python-pip python-wheel vim git archlinux-keyring
pacman --noconfirm -Su
pacman --noconfirm -Sc

rm -f  /home/*/.bash_history /root/.bash_history

"""

NEWPKG = Path('boxes') / f"arch64-{datetime.today().strftime('%Y.%m.%d')}.box"

with TemporaryDirectory() as tmpd:
    tmpd = Path(tmpd)
    print(tmpd)

    print("Creating Vagrantfile")
    print(VAGRANT_FILE)

    (tmpd / 'Vagrantfile').write_text(VAGRANT_FILE)
    (tmpd / 'setup.sh').write_text(SETUP_SH)

    check_call(['vagrant', 'up'], cwd=tmpd)

    check_call(['vagrant', 'package', '--output', NEWPKG.absolute()], cwd=tmpd)

    check_call(['vagrant', 'destroy', '--force'], cwd=tmpd)
