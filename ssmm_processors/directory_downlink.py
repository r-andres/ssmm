from kaitai.juice_ccsds import JuiceCcsds
from ssmm_processors.processors import Processor


class DirectoryDownlinkProcessor(Processor):

    def process(self, packet):
        data = self.dd_processor(packet.payload)
        self.items.append(self.build_item(packet, data))



    def dd_processor(self, payload: JuiceCcsds.DirectoryDownlink):

        item = {
            "number_of_directories": payload.num_directories
        }
        for entry in payload.directories:
            item[entry.directory_id] = {
                "directory_id": entry.directory_id,
                "state":  "ENABLED" if entry.state == 1 else "DISABLED",
                "priority":  entry.priority,
                "rf_band": "x" if entry.rf_band == 0 else "ka"
            }
        return item