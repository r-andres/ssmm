from kaitai.juice_ccsds import JuiceCcsds
from ssmm_processors.processors import Processor
from ssmm_processors.utils import cuc_to_utc, file_id_hex
from tm_processor.spice.time_utils import get_cuc_time_48_bits

class FileStatusProcessor(Processor):

    TWIN_THRESHOLD_SECONDS = 2
    PARTITIONS = [b'\x0c']

    def __init__(self, file, packet_class):
        super().__init__(file, packet_class)
        self.previous_coarse = 0


    def process(self, packet: JuiceCcsds.Packet):
        cuc_coarse, _ = get_cuc_time_48_bits(packet.pus_header.sc_time)
        utc = cuc_to_utc(packet.pus_header.sc_time)
        data = self.fs_processor(packet.payload)

        if packet.payload.partition_id not in self.PARTITIONS:
            self.logger.warning("Skipping packet: Partition non valid")
            return

        if abs(self.previous_coarse - cuc_coarse) < self.TWIN_THRESHOLD_SECONDS:
            self.logger.info("Twin packet")

            previous_item = self.items[-1]
            previous_data = previous_item.get("data")
            previous_data.update(data)

            previous_item["twin"] = previous_item.get("twin", [previous_item.get("timestamp")])
            previous_item["twin"].append(utc)
        else:
            self.items.append(self.build_item(packet, data))
        
        self.previous_coarse = cuc_coarse


    def fs_processor(self, payload: JuiceCcsds.FileStatus):
        MODE_MAP = {
                0: "CLOSED",
                1: "OPEN",
        }

        PROTECT_MAP = {
            0: "DISABLED",
            1: "ENABLED",
        }
    
        item = {}        
        for entry in payload.files:
            directory_id = entry.directory_id
            file_id = file_id_hex(entry.file_id)
            if directory_id not in item:
                item[directory_id] = {}
            directory = item[directory_id]
            directory[file_id] = {
                "file_id": file_id,
                "file_address": entry.file_address,
                "file_size": entry.file_size,
                "file_type": entry.file_type,
                "file_protect_status": PROTECT_MAP[entry.file_protect_status],
                "file_mode": MODE_MAP[entry.file_mode],
                "creation_time": cuc_to_utc(entry.creation_time_cuc) 
            }
        return item

    def calculate_metadata(self):
        for entry in self.items:
            data = entry.get("data")
            entry["metadata"] = {
                "number_of_directories": len(data.keys()),
                "number_of_files": sum([len(directory.keys()) for directory in data.values()])

                }
            
    def build_item(self, packet, item):
        build = super().build_item(packet, item)
        return build