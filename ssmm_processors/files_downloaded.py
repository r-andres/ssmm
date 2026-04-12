from kaitai.juice_ccsds import JuiceCcsds
from ssmm_processors.processors import Processor
from ssmm_processors.utils import file_id_hex, cuc_to_utc, duration_seconds
from tm_processor.spice.time_utils import get_cuc_time_48_bits

class FilesDownloadedProcessor(Processor):

    def __init__(self, file, packet_class):
        super().__init__(file, packet_class)
        self.processing_ka = None
        self.processed_ka = []
        self.items = ['active']



    def process(self, packet: JuiceCcsds.Packet):
        cuc_coarse, _ = get_cuc_time_48_bits(packet.pus_header.sc_time)
        utc = cuc_to_utc(packet.pus_header.sc_time)
        data = self.rt_processor(utc, packet.payload)
        if data is not None:
            self.items.append(self.build_item(packet, data))



    def rt_processor(self, utc: str, payload: JuiceCcsds.RealTimeDownlink):

        SESSION_ACTIVE = 2

        if payload.cfdp_ka_session_state != SESSION_ACTIVE and payload.cfdp_x_session_state != SESSION_ACTIVE:
            return None
        item = {}
        if payload.cfdp_ka_session_state == SESSION_ACTIVE and payload.cfdp_ka_current_file_id != 0:
            file_id = file_id_hex(payload.cfdp_ka_current_file_id)
            ka_file = {
                "directory_id": payload.cfdp_ka_current_directory_id,
                "file_id": file_id_hex(payload.cfdp_ka_current_file_id),
                "start": utc,
                "end": utc
            }
            if self.processing_ka:
                if file_id == self.processing_ka.get('file_id'):
                    # TODO control the timing of the last packet
                    ka_file['start'] = self.processing_ka.get('start')
                else:
                    print( 'OK' if self.processing_ka.get('start') < self.processing_ka.get('end') else 'AGGG')
                    self.processing_ka['duration'] = duration_seconds(self.processing_ka.get('start'), self.processing_ka.get('end'))
                    self.processed_ka.append(self.processing_ka)
            self.processing_ka = ka_file

        return item
    
    def calculate_metadata(self):
        self.items = []
        self.items.extend(self.processed_ka + [self.processing_ka])
