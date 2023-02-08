# -*- mode: python ; coding: utf-8 -*-


block_cipher = None


a = Analysis(['main_gui.py'], 
             pathex=['/home/celis/Documents/atoms30/trunk/PROJECTS/PAA/eSCAN/Simulator'],
             binaries=[],
	         datas=[],
             hiddenimports=['pandas._libs.tslibs.base','matplotlib'],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          [],
          name='main_gui',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          upx_exclude=[],
          runtime_tmpdir=None,
          console=True )
