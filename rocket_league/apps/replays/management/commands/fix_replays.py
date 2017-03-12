import os

import re
import boto
from boto.s3.connection import S3Connection
from boto.s3.connection import OrdinaryCallingFormat
from django.core.management.base import BaseCommand

from ...models import Replay as ReplayModel
from django.conf import settings
from pyrope import Replay


class Command(BaseCommand):

    def handle(self, *args, **options):
        ids = [79, 328, 329, 383, 407, 516, 598, 602, 679, 680, 736, 817, 841, 842, 843, 844, 845, 846, 847, 848, 849, 850, 851, 852, 853, 857, 1025, 2138, 2405, 2597, 2713, 2885, 3344, 3987, 4110, 4252, 4653, 4742, 4743, 4744, 4745, 4746, 5019, 5110, 5216, 5217, 5218, 6007, 6009, 6026, 6802, 6803, 6804, 6809, 6810, 6811, 6818, 6819, 6820, 6821, 6822, 6839, 6840, 6842, 6874, 6875, 6876, 6877, 6878, 6879, 6880, 6881, 6882, 7013, 7209, 7211, 7369, 7630, 8727, 11008, 11009, 11010, 11011, 11012, 11013, 11014, 11015, 11016, 11017, 11018, 11019, 11020, 11021, 11022, 11023, 11024, 11025, 11026, 11027, 11028, 11029, 11030, 11031, 11032, 11033, 11034, 11035, 11036, 11037, 11038, 11039, 11040, 11041, 11042, 11043, 11044, 11045, 11046, 11047, 11048, 11049, 11050, 11051, 11052, 11053, 11054, 11055, 11056, 11057, 11058, 11059, 11060, 11061, 11062, 11063, 12173, 14799, 16364, 16976, 17166, 17274, 17275, 17276, 17278, 17281, 21851, 21864, 21919, 22009, 22038, 23336, 23337, 25799, 27277, 29572, 30730, 31180, 31181, 31182, 31183, 31185, 31186, 31189, 31190, 31191, 31193, 31194, 31195, 31196, 31197, 31198, 31199, 31200, 31201, 31202, 31204, 31205, 31206, 31207, 31208, 31209, 31210, 31211, 31212, 31213, 31214, 31215, 31217, 31218, 31219, 31220, 31221, 31222, 31223, 31224, 31225, 31226, 31227, 31228, 32260, 32262, 34471, 36447, 36448, 36676, 36678, 36679, 36680, 36681]

        # Match the files which aren't UUIDs.
        exp = re.compile(r'^uploads\/replay_files\/[A-F0-9]{8}4[A-F0-9]{23}\.replay$')

        conn = boto.s3.connect_to_region('eu-west-1', aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'), aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'), calling_format=OrdinaryCallingFormat())
        bucket = conn.get_bucket('media.rocketleaguereplays.com')
        s3_files = [
            key.name.replace('uploads/replay_files/', '')
            for key in bucket.list(prefix='uploads/replay_files')
            if re.match(exp, key.name) is None and
            key.name != 'uploads/replay_files/'
        ]

        # Now we need to parse the header for each of these files and determine
        # what their replay ID is.

        replay_mappings = {}

        for s3_file in s3_files:
            local_file_path = os.path.join(settings.MEDIA_ROOT, 'uploads/replay_files', s3_file)

            with open(local_file_path, 'rb') as f:
                try:
                    replay = Replay(f.read())
                    replay_mappings[replay.header['Id']] = s3_file
                except:
                    pass

        for i in ids:
            r = ReplayModel.objects.get(pk=i)

            if r.replay_id in replay_mappings:
                print('Replay.objects.get(pk={}).update(file="uploads/replay_files/{}")'.format(i, replay_mappings[r.replay_id]))
            else:
                print('#', i, 'not found :(')
