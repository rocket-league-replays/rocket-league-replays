#!/usr/bin/env python3
import os
import sys

import requests
from distutils.version import StrictVersion

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "rocket_league.settings.local")

    from django.core.management import execute_from_command_line

    version_blacklist = []

    # Ensure Rattletrap is kept up-to-date.
    if len(sys.argv) > 1 and 'runserver' in sys.argv[1] and os.getenv('GITHUB_TOKEN', False):
        rattletrap_release = requests.get('https://api.github.com/repos/tfausak/rattletrap/releases/latest', headers={
            'Authorization': 'Token {}'.format(os.getenv('GITHUB_TOKEN', ''))
        }).json()

        # What version do we have locally?
        try:
            os.remove('rattletrap-binaries/.DS_Store')
        except FileNotFoundError:
            pass

        current_binaries = os.listdir('rattletrap-binaries')

        current_version = '0.0.0'

        if len(current_binaries) > 0:
            current_version = current_binaries[0].split('-')[1]

        print('GH: {}. RLR: {}. Update? {}'.format(
            rattletrap_release['name'],
            current_version,
            'Yes' if StrictVersion(rattletrap_release['name']) > StrictVersion(current_version) else 'No'
        ))

        if StrictVersion(rattletrap_release['name']) > StrictVersion(current_version):
            if rattletrap_release['name'] in version_blacklist:
                print('Skipping this version.')
            else:
                # Download the latest version.
                for file in current_binaries:
                    os.remove('rattletrap-binaries/{}'.format(file))

                for asset in rattletrap_release['assets']:
                    if 'windows' in asset['browser_download_url']:
                        continue

                    print('Downloading {}'.format(asset['name']))

                    os.system('wget -qP rattletrap-binaries/ {} && gunzip -f rattletrap-binaries/{} && chmod +x rattletrap-binaries/{}'.format(
                        asset['browser_download_url'],
                        asset['name'],
                        asset['name'].replace('.gz', ''),
                    ))

    execute_from_command_line(sys.argv)
