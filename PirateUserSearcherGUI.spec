# -*- mode: python ; coding: utf-8 -*-
a = Analysis(
    ['PirateUserSearcherGUI.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('C:/Users/WBPC/AppData/Local/Programs/Python/Python313/Lib/site-packages/Pmw', 'Pmw'),
        ('C:/Users/WBPC/AppData/Local/Programs/Python/Python313/tcl/tcl8.6', 'tcl'),
        ('C:/Users/WBPC/AppData/Local/Programs/Python/Python313/tcl/tk8.6', 'tk'),
        ('Resources/storm.jpg', 'Resources'),
        ('Resources/pirate.png', 'Resources'),
        ('Resources/home.png', 'Resources'),
        ('Resources/form.png', 'Resources'),
        ('Resources/delete.png', 'Resources'),
        ('Resources/search.png', 'Resources'),
        ('Resources/back.png', 'Resources'),
        ('Resources/coffee.png', 'Resources'),
        ('Resources/selected.png', 'Resources'),
        ('Resources/unselected.png', 'Resources'),
        ('Resources/harle.json', 'Resources'),
        ('Resources/pirate.ico', 'Resources')
    ],
    hiddenimports=['Pmw', 'Pmw.Balloon', 'tkinter', 'customtkinter', 'Pmw.Color', 'Pmw.MessageDialog', 'Pmw.ScrolledText', 'PIL', 'PIL.Image', 'PIL.ImageTk'],
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
    name='PirateUserSearcherGUI',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # Set to False for no console window
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='Resources/pirate.ico'  # Specify the icon file
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='PirateUserSearcherGUI',
)