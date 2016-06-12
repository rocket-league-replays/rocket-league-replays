#!/usr/bin/env python2.7
import os
import sys

import requests

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "rocket_league.settings.local")

    from django.core.management import execute_from_command_line

    version_blacklist = ['0.8.0']

    # Ensure Octane is kept up-to-date.
    if 'runserver' in sys.argv[1]:
        octane_release = requests.get('https://api.github.com/repos/tfausak/octane/releases/latest', headers={
            'Authorization': 'Token {}'.format(os.getenv('GITHUB_TOKEN', ''))
        }).json()

        # What version do we have locally?
        try:
            os.remove('octane-binaries/.DS_Store')
        except FileNotFoundError:
            pass

        current_binaries = os.listdir('octane-binaries')

        current_version = '0.0.0'

        if len(current_binaries) > 0:
            current_version = current_binaries[0].split('-')[1]

        print('GH: {}. RLR: {}'.format(octane_release['name'], current_version))

        if tuple(octane_release['name'].split('.')) > tuple(current_version.split('.')):
            if octane_release['name'] in version_blacklist:
                print('Skipping this version.')
            else:
                # Download the latest version.
                for file in current_binaries:
                    os.remove('octane-binaries/{}'.format(file))

                for asset in octane_release['assets']:
                    if 'windows' in asset['browser_download_url']:
                        continue

                    print('Downloading {}'.format(asset['name']))

                    os.system('wget -qP octane-binaries/ {} && gunzip -f octane-binaries/{} && chmod +x octane-binaries/{}'.format(
                        asset['browser_download_url'],
                        asset['name'],
                        asset['name'].replace('.gz', ''),
                    ))

    execute_from_command_line(sys.argv)
