from kaitai.juice_ccsds import JuiceCcsds
from ssmm_processors.processors import Processor


class DirectoryDownlinkProcessor(Processor):

    def process(self, packet):
        data = self.dd_processor(packet.payload)
        self.items.append(self.build_item(packet, data))



    def dd_processor(self, payload: JuiceCcsds.DirectoryDownlink):

        item = {}

        for entry in payload.directories:
            item[entry.directory_id] = {
                "directory_id": entry.directory_id,
                "state":  "ENABLED" if entry.state == 1 else "DISABLED",
                "priority":  entry.priority,
                "rf_band": "x" if entry.rf_band == 0 else "ka"
            }
        return item
    
    def calculate_metadata(self):
        for entry in self.items:
            data = entry.get("data")
            entry["metadata"] = {
                "number_of_directories": len(data.keys()),
                "using_ka": [ directory.get('directory_id') for directory in data.values() if directory.get("rf_band") == "ka"],
                "using_x": [ directory.get('directory_id') for directory in data.values() if directory.get("rf_band") == "x"]
                }