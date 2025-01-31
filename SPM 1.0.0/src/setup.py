from setuptools import setup

APP = ['main.py']
DATA_FILES = [
    ('resources/icons', [
        'resources/icons/eyeClose_icon.png',
        'resources/icons/eyeOpen_icon.png',
        'resources/icons/loading_icon.gif',
        'resources/icons/lock_icon.png',
        'resources/icons/web_icon.png',
    ]),
    ('resources/fonts', [
        'resources/fonts/CourierPrime-Regular.ttf',
    ]),
]
OPTIONS = {
    'argv_emulation': True,
    'packages': [
        'PyQt6',
        'cryptography',
        'SQLAlchemy',
        'argon2_cffi',
        'requests',
        'beautifulsoup4',
    ],
}

setup(
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
