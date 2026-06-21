# -*- mode: python ; coding: utf-8 -*-
import os, shutil
from PyInstaller.utils.hooks import collect_all

datas = []
binaries = [('D:\\projects\\ytgrap\\ffmpeg_bin\\ffmpeg.exe', 'ffmpeg_bin'), ('D:\\projects\\ytgrap\\ffmpeg_bin\\ffprobe.exe', 'ffmpeg_bin')]
hiddenimports = ['yt_dlp']
tmp_ret = collect_all('yt_dlp')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]


a = Analysis(
    ['D:\\projects\\ytgrap\\youtube_downloader.py'],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='YTGrab',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['D:\\projects\\ytgrap\\ytgrab_icon.ico'],
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='YTGrab',
)

python_dir = r'C:\Python314'
dist_dir = os.path.join(SPECPATH, 'dist', 'YTGrab')
for dll in ['python3.dll', 'vcruntime140.dll', 'vcruntime140_1.dll']:
    src = os.path.join(python_dir, dll)
    dst = os.path.join(dist_dir, dll)
    if os.path.exists(src):
        shutil.copy2(src, dst)
