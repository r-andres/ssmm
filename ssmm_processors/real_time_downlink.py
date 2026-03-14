from kaitai.juice_ccsds import JuiceCcsds
from ssmm_processors.processors import Processor
from ssmm_processors.utils import file_id_hex


class RealTimeDownlinkProcessor(Processor):

    def process(self, packet):
        data = self.rt_processor(packet.payload)
        self.items.append(self.build_item(packet, data))



    def rt_processor(self,payload: JuiceCcsds.RealTimeDownlink):

        SESSION_ACTIVE = 2
        STATE_MAP = {
                0: "INACTIVE",
                1: "SUSPENDED",
                2: "RUNNING"
        }

        if payload.cfdp_ka_session_state != SESSION_ACTIVE and payload.cfdp_x_session_state != SESSION_ACTIVE:
            return None
        item = {}
        if payload.cfdp_ka_session_state == SESSION_ACTIVE:
            item["ka"] = {
                "state": STATE_MAP[payload.cfdp_ka_session_state],
                "open_transactions": payload.cfdp_numberoftrans_ka
            }
            if payload.cfdp_ka_current_file_id != 0:
                item["ka"]["transmitting"] = {
                    "directory_id": payload.cfdp_ka_current_directory_id,
                    "file_id": file_id_hex(payload.cfdp_ka_current_file_id)
                }
        if payload.cfdp_x_session_state == SESSION_ACTIVE:
            item["x"] = {
                "state": STATE_MAP[payload.cfdp_x_session_state],
                "open_transactions": payload.cfdp_numberoftrans_x
            }
            if payload.cfdp_x_current_file_id != 0:
                item["x"]["transmitting"] = {
                    "directory_id": payload.cfdp_x_current_directory_id,
                    "file_id": file_id_hex(payload.cfdp_x_current_file_id)
                }

        return item