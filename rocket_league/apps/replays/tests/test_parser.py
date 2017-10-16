import os

from django.conf import settings
from django.core.files import File
from django.test import TestCase
from django.test.utils import override_settings

from pyrope.exceptions import PropertyParsingError

from ..models import Replay


class TestReplayParser(TestCase):

    # ['',  pyrope.exceptions.PropertyParsingError]
    replays = [
        ['00090006000500070021021B99DF8BA2', None],
        ['0AD21FEE4A512906BEB6C98136AAF49A', None],
        ['1A126AC24CAA0DB0E98835BD960B8AF8', None],
        ['1AE415514DFC65DCBF8B8391AD35488D', None],
        ['1BC2D01444ACE577D01E988EADD4DFD0', None],
        ['1D1DE97D4941C86E43FE0093563DB621', None],
        ['1EF90FCC4F719F606A5327B3CDD782A4', None],
        ['1F3798E540B0C37A946561ABBB3037F9', None],
        ['3EA147DD485B8DD24810689A7A989E44', None],
        ['6B0D1614417085A7AAD82EAA30D8DABE', None],
        ['6B111DEA41797216FFA7D3B01B225006', None],
        ['6D1B06D844A5BB91B81FD4B5B28F08BA', None],
        ['6F7CFCD24638F8A6567AB3A8B9958A90', None],
        ['7BF6073F4614CE0A438994B9A260DA6A', None],
        ['07E925B1423653D44CB8B4B2524792C1', None],
        ['8AE551FF406D7B82ED853B8C7BFF8CDA', None],
        ['9A93C12646BB2517DFCE19B514B85CA8', None],
        ['010D2D7944D262BC2AAF2FA5DD23AA6E', None],
        ['16D580EF479483E015207C901776F9FB', None],
        ['18D6738D415B70B5BE4C299588D3C141', None],
        ['22BACD794ABE7B92E50E9CBDBD9C59CE', None],
        ['27B6A7B64553F0F685874584F96BAB1B', None],
        ['29F582C34A65EB34D358A784CBE3C189', None],
        ['42F0D8DA4FC89AE7B80FCAB7F637A8EA', None],
        ['52AA67F94090C19D33C5009E54D31FE4', None],
        ['89CBA30E46FA5385BDD35DA4285D4D2E', None],
        ['98E58A904D713F2DE202358E8573265D', None],
        ['160CA83E41083BFD8E6315B4BFCA0561', None],
        ['372DBFCA4BDB340E4357B6BD43032802', None],
        ['387F059C47C09E253C875CA990EFD9F2', None],
        ['504ED825482186E771FAA9B642CE5CE4', None],
        ['520E1BFF468CF6C3C48D1EA85D9C7909', None],
        ['540DA764423C8FB24EB9D486D982F16F', None],
        ['551CA4D44FF2B86015DE44A6B5790D4C', None],
        ['1205D96C4D819800927791820096CD49', None],
        ['6320E51C49066A7C210A2993C2201D5F', None],
        ['6688EEE34BFEB3EC3A9E3283098CC712', PropertyParsingError],
        ['7109EB9846D303E54B7ACBA792036213', None],
        ['22660E3649FC7971E5653692473D4318', None],
        ['211466D04B983F5A33CC2FA1D5928672', None],
        ['512256CE4C695326BB8E5AAA4680A293', None],
        ['772810F44196DADD653608A44146D167', None],
        ['4126861E477F4A03DE2A4080374D7908', None],
        ['6790915F4216FEC5E6EBB089D3BA6FF0', None],
        ['338173964F9F71EBDD31058A1936CBB4', None],
        ['9704208245D7DD851F2FB2BC7DFD9AC3', None],
        ['00080014003600090000036E0F65CCEB', None],
        ['A7F001A1417A19BFA8C90990D8F7C2FF', None],
        ['A52F804845573D8DA65E97BF59026A43', None],
        ['A128B3AB45D5A18E3EF9CF93C9576BCE', None],
        ['A558B1B44124D6E021640884E8EEC2A7', None],
        ['A993D8E2447A0887F49234AF27399379', None],
        ['A6711CE74272B2E663DCC9A200A218E3', None],
        ['AFB1F46A49737E36928E1EABC6F5B7AD', None],
        ['B9F9B87D4A9D0A3D25D4EC91C0401DE2', None],
        ['C14F7E0E4D9B5E6BE9AD5D8ED56B174C', None],
        ['C8372B1345B1803DEF039F815DBD802D', None],
        ['CC4CA70D4F7A67EBAD0ED9B9923106F7', None],
        ['D7FB197A451D69075A0C99A2F49A4053', None],
        ['D428F81646A98C25902CE988AE5C14C8', None],
        ['D0449F5F4AA775B86FFA7DA2B5A3204E', None],
        ['DCB3A6B94A9DBE46FDE5EAA9B012F6C8', None],
        ['EAE8DADA4BB2DC5422792C9B4A67392D', None],
        ['EAE311E84BA35B590A6FDBA6DD4F2FEB', None],
        ['F7B9E14545C7467B89A00895980FCD73', None],
        ['F299F176491554B11E34AB91CA76B2CE', None],
        ['F811C1D24888015E23B598AD8628C742', None],
        ['FDC79DA84DD463D4BCCE6B892829AC88', None],
    ]

    def _save_replay(self, replay_id):
        base_dir = os.path.join(settings.SITE_ROOT, 'apps/replays/tests/replays')

        with open(os.path.join(base_dir, '{}.replay'.format(replay_id)), 'rb') as f:
            # Test the standard header
            r = Replay.objects.create(
                file=File(f),
            )

            # Test parsing the netstream
            r.save(parse_netstream=True)

    @override_settings(DEBUG=True)
    def _test_replay(self, replay_id, exception_class):
        if exception_class:
            with self.assertRaises(exception_class):
                self._save_replay(replay_id)
        else:
            self._save_replay(replay_id)

    @override_settings(DEBUG=True)
    def test_replays(self):
        for replay_id, exception_class in self.replays:
            self._test_replay(replay_id, exception_class)
