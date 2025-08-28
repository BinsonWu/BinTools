#!/bin/bash

python3 -m pip install pyinstaller
python3 -m PyInstaller --onefile \
    --add-binary "/usr/lib/x86_64-linux-gnu/libpython3.10.so.1.0:." \
    --add-binary "/lib/x86_64-linux-gnu/libdl.so.2:." \
    --add-binary "/lib/x86_64-linux-gnu/libz.so.1:." \
    --add-binary "/lib/x86_64-linux-gnu/libpthread.so.0:." \
    --add-binary "/lib/x86_64-linux-gnu/libc.so.6:." \
    SvnController.py
sudo cp -f dist/SvnController ./SvnController
sudo chmod 777 ./SvnController
sudo cp -f dist/SvnController /usr/local/bin/SvnController
sudo chmod 777 /usr/local/bin/SvnController
