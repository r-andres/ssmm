# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild

import kaitaistruct
from kaitaistruct import KaitaiStruct, KaitaiStream, BytesIO


if getattr(kaitaistruct, 'API_VERSION', (0, 9)) < (0, 9):
    raise Exception("Incompatible Kaitai Struct Python API: 0.9 or later is required, but you have %s" % (kaitaistruct.__version__))

class JuiceCcsds(KaitaiStruct):
    def __init__(self, _io, _parent=None, _root=None):
        self._io = _io
        self._parent = _parent
        self._root = _root if _root else self
        self._read()

    def _read(self):
        self.packets = []
        i = 0
        while not self._io.is_eof():
            self.packets.append(JuiceCcsds.Packet(self._io, self, self._root))
            i += 1


    class UnknowPayload(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.data = self._io.read_bytes_full()


    class DdsSection(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.seconds = self._io.read_u4be()
            self.microseconds = self._io.read_u4be()
            self.len_packet_data = self._io.read_u4be()
            self.ground_station = self._io.read_u2be()
            self.virtual_channel = self._io.read_u2be()
            self.sle_type = self._io.read_u1()
            self.time_quality = self._io.read_u1()


    class DirectoryDownlink(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.num_directories = self._io.read_u4be()
            self.directories = []
            for i in range(self.num_directories):
                self.directories.append(JuiceCcsds.DirectoryDownlinkEntry(self._io, self, self._root))



    class FileStatus(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.partition_id = self._io.read_bytes(1)
            self.num_files = self._io.read_u2be()
            self.files = []
            for i in range(self.num_files):
                self.files.append(JuiceCcsds.File(self._io, self, self._root))



    class CcsdsPrimaryHeader(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.version_number = self._io.read_bits_int_be(3)
            self.packet_type = self._io.read_bits_int_be(1) != 0
            self.secondary_header_flag = self._io.read_bits_int_be(1) != 0
            self.apid = self._io.read_bits_int_be(11)
            self.sequence_flags = self._io.read_bits_int_be(2)
            self.sequence_counter = self._io.read_bits_int_be(14)
            self._io.align_to_byte()
            self.packet_length = self._io.read_u2be()


    class DirectorySetupEntry(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.directory_id = (self._io.read_bytes(4)).decode(u"ASCII")
            self.max_dir_size = self._io.read_u4be()
            self.max_file_size = self._io.read_u4be()
            self.max_wrt_timeout = self._io.read_u4be()
            self.max_wrt_speed = self._io.read_u4be()


    class File(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.directory_id = (self._io.read_bytes(4)).decode(u"ASCII")
            self.file_id = self._io.read_u4be()
            self.file_address = self._io.read_u4be()
            self.file_size = self._io.read_u4be()
            self.file_type = self._io.read_u4be()
            self.file_protect_status = self._io.read_u4be()
            self.file_mode = self._io.read_u4be()
            self.creation_time_cuc = self._io.read_bytes(6)


    class RealTimeDownlink(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.hk_structure_id = self._io.read_u4be()
            self.ldt_reception_timeout = self._io.read_u4be()
            self.ft1_numberexpectedsdu = self._io.read_u4be()
            self.ft1_ldu_id = self._io.read_u4be()
            self.ft1_numberreceivedsdu = self._io.read_u4be()
            self.ft1_uplink_state = self._io.read_bytes(4)
            self.ft2_numberexpectedsdu = self._io.read_u4be()
            self.ft2_ldu_id = self._io.read_u4be()
            self.ft2_numberreceivedsdu = self._io.read_u4be()
            self.ft2_uplink_state = self._io.read_bytes(4)
            self.cfdp_ka_downlink_rate = self._io.read_u4be()
            self.cfdp_ka_session_state = self._io.read_u1()
            self.cfdp_ka_current_directory_id = (self._io.read_bytes(4)).decode(u"ASCII")
            self.cfdp_ka_current_file_id = self._io.read_u4be()
            self.cfdp_numberoftrans_ka = self._io.read_u4be()
            self.cfdp_x_downlink_rate = self._io.read_u4be()
            self.cfdp_x_session_state = self._io.read_u1()
            self.cfdp_x_current_directory_id = (self._io.read_bytes(4)).decode(u"ASCII")
            self.cfdp_x_current_file_id = self._io.read_u4be()
            self.cfdp_numberoftrans_x = self._io.read_u4be()


    class DirectoryDownlinkEntry(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.partition = self._io.read_bytes(1)
            self.directory_id = (self._io.read_bytes(4)).decode(u"ASCII")
            self.state = self._io.read_u1()
            self.priority = self._io.read_u1()
            self.rf_band = self._io.read_u1()


    class PusSecondaryHeader(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.spare = self._io.read_bits_int_be(1) != 0
            self.pus_version = self._io.read_bits_int_be(3)
            self.spare2 = self._io.read_bits_int_be(4)
            self._io.align_to_byte()
            self.service_type = self._io.read_u1()
            self.service_subtype = self._io.read_u1()
            self.destination = self._io.read_u1()
            self.sc_time = self._io.read_bytes(6)


    class Packet(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.dds = JuiceCcsds.DdsSection(self._io, self, self._root)
            self.primary_header = JuiceCcsds.CcsdsPrimaryHeader(self._io, self, self._root)
            self.pus_header = JuiceCcsds.PusSecondaryHeader(self._io, self, self._root)
            _on = ((self.pus_header.service_type << 8) | self.pus_header.service_subtype)
            if _on == 40721:
                self._raw_payload = self._io.read_bytes((self.dds.len_packet_data - 16))
                _io__raw_payload = KaitaiStream(BytesIO(self._raw_payload))
                self.payload = JuiceCcsds.DirectoryDownlink(_io__raw_payload, self, self._root)
            elif _on == 36870:
                self._raw_payload = self._io.read_bytes((self.dds.len_packet_data - 16))
                _io__raw_payload = KaitaiStream(BytesIO(self._raw_payload))
                self.payload = JuiceCcsds.FileStatus(_io__raw_payload, self, self._root)
            elif _on == 793:
                self._raw_payload = self._io.read_bytes((self.dds.len_packet_data - 16))
                _io__raw_payload = KaitaiStream(BytesIO(self._raw_payload))
                self.payload = JuiceCcsds.RealTimeDownlink(_io__raw_payload, self, self._root)
            elif _on == 43547:
                self._raw_payload = self._io.read_bytes((self.dds.len_packet_data - 16))
                _io__raw_payload = KaitaiStream(BytesIO(self._raw_payload))
                self.payload = JuiceCcsds.DirectorySetup(_io__raw_payload, self, self._root)
            else:
                self._raw_payload = self._io.read_bytes((self.dds.len_packet_data - 16))
                _io__raw_payload = KaitaiStream(BytesIO(self._raw_payload))
                self.payload = JuiceCcsds.UnknowPayload(_io__raw_payload, self, self._root)


    class DirectorySetup(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.partition_id = self._io.read_u1()
            self.num_directories = self._io.read_u4be()
            self.directories = []
            for i in range(self.num_directories):
                self.directories.append(JuiceCcsds.DirectorySetupEntry(self._io, self, self._root))




