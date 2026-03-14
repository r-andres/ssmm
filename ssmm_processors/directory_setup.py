from kaitai.juice_ccsds import JuiceCcsds
from ssmm_processors.processors import Processor


class DirectorySetupProcessor(Processor):

    def process(self, packet):
        self.items.append(self.ds_processor(packet.payload))


    def ds_processor(self,payload: JuiceCcsds.DirectorySetup):

        item = {
            "number_of_directories": payload.num_directories
        }
        for entry in payload.directories:
            item[entry.directory_id] = {
                "directory_id": entry.directory_id,
                "max_dir_size": entry.max_dir_size,
                "max_file_size": entry.max_file_size,
                "max_wrt_timeout": entry.max_wrt_timeout,
                "max_wrt_speed": entry.max_wrt_speed
            }
        return item