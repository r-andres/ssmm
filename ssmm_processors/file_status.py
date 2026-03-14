from kaitai.juice_ccsds import JuiceCcsds
from ssmm_processors.processors import Processor
from ssmm_processors.utils import cuc_to_utc, file_id_hex


class FileStatusProcessor(Processor):

    def process(self, packet):
        self.items.append(self.fs_processor(packet.payload))


    def fs_processor(self, payload: JuiceCcsds.FileStatus):
        item = {
            "number_of_files": payload.num_files
        }
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
                "file_protect_status": entry.file_protect_status,
                "file_mode": entry.file_mode,
                "creation_time_cuc": cuc_to_utc(entry.creation_time_cuc) 
            }
        return item