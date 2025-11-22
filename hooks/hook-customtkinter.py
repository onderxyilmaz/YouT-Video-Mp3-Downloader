"""
PyInstaller hook for customtkinter
"""
from PyInstaller.utils.hooks import collect_all, collect_submodules, copy_metadata

# Collect everything from customtkinter
datas, binaries, hiddenimports = collect_all('customtkinter')

# Ensure all submodules are included
hiddenimports += collect_submodules('customtkinter')

# Add specific submodules that might be missed
hiddenimports += [
    'customtkinter.windows',
    'customtkinter.windows.widgets',
    'customtkinter.windows.widgets.core_rendering',
    'customtkinter.windows.widgets.core_widget_classes',
    'customtkinter.windows.widgets.font',
    'customtkinter.windows.widgets.image',
    'customtkinter.windows.widgets.scaling',
    'customtkinter.windows.widgets.theme',
    'customtkinter.windows.widgets.utility',
]
