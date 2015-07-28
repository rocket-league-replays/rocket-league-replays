import pprint
import re
import struct


class ReplayParser(object):

    debug = False

    def parse(self, obj):
        if hasattr(obj, 'read'):
            replay_file = obj
        else:
            replay_file = open(obj.file.path, 'rb')

        replay_file.seek(44, 1)

        results = self._read_properties(replay_file)
        results = self.manual_parse(results, replay_file)

        if self.debug:
            pprint.pprint(results)

        return results

    def _read_properties(self, replay_file):
        results = {}

        while True:
            property_info = self._read_property(replay_file)
            if property_info:
                results[property_info['name']] = property_info['value']
            else:
                return results

    def _read_property(self, replay_file):
        if self.debug:
            print("Reading name")

        name_length = self._read_integer(replay_file, 4)
        property_name = self._read_string(replay_file, name_length)

        if self.debug:
            print("Property name: {}".format(property_name))

        if property_name == 'None':
            return None

        if self.debug:
            print("Reading type")

        type_length = self._read_integer(replay_file, 4)
        type_name = self._read_string(replay_file, type_length)

        if self.debug:
            print("Type name: {}".format(type_name))

        if self.debug:
            print("Reading value")

        if type_name == 'IntProperty':
            value_length = self._read_integer(replay_file, 8)
            value = self._read_integer(replay_file, value_length)
        elif type_name == 'StrProperty':
            replay_file.seek(8, 1)
            length = self._read_integer(replay_file, 4)
            value = self._read_string(replay_file, length)
        elif type_name == 'FloatProperty':
            length = self._read_integer(replay_file, 8)
            value = self._read_float(replay_file, length)
        elif type_name == 'NameProperty':
            replay_file.seek(8, 1)
            length = self._read_integer(replay_file, 4)
            value = self._read_string(replay_file, length)
        elif type_name == 'ArrayProperty':
            # I imagine that this is the length of bytes that the data
            # in the "array" actually take up in the file.
            replay_file.seek(8, 1)
            array_length = self._read_integer(replay_file, 4)

            value = [
                self._read_properties(replay_file)
                for x in range(array_length)
            ]

        if self.debug:
            print("Value: {}".format(value))

        return {
            'name': property_name,
            'value': value
        }

    def _print_bytes(self, bytes_read):
        if self.debug:
            print('Hex read: ' + ':'.join(hex(ord(x)) for x in bytes_read))

    def _read_integer(self, replay_file, length):
        number_format = {
            1: '<B',
            2: '<H',
            4: '<I',
            8: '<Q',
        }[length]
        bytes_read = replay_file.read(length)
        self._print_bytes(bytes_read)
        value = struct.unpack(number_format, bytes_read)[0]
        if self.debug:
            print("Integer read: {}".format(value))
        return value

    def _read_float(self, replay_file, length):
        number_format = {
            4: '<f',
            8: '<d'
        }[length]
        bytes_read = replay_file.read(length)
        self._print_bytes(bytes_read)
        value = struct.unpack(number_format, bytes_read)[0]
        if self.debug:
            print("Float read: {}".format(value))
        return value

    def _read_unknown(self, replay_file, num_bytes):
        bytes_read = replay_file.read(num_bytes)
        self._print_bytes(bytes_read)
        return bytes_read

    def _read_string(self, replay_file, length):
        bytes_read = replay_file.read(length)[:-1]
        self._print_bytes(bytes_read)
        return bytes_read

    # Temporary method while we learn the replay format.
    def manual_parse(self, results, replay_file):
        server_regexp = re.compile(r'((?:EU|USE|USW|OCE)\d+-[A-Z][a-z]+)')

        search = server_regexp.search(replay_file.read())
        if search:
            results['ServerName'] = search.group()

        return results
