from pathlib import Path
import json
import logging

from ssmm_processors.utils import cuc_to_utc


class Processor:

    logger = logging.getLogger(__name__)

    def __init__(self, file, packet_class):
        self.file = file
        self.items = []
        self.packet_class = packet_class

    def process(self, packet):
        pass

    def dump(self):
        if len(self.items) > 0:
            self.calculate_metadata()

            output_file = Path(self.file).with_suffix(f".{self.packet_class.__name__}.json")
            with output_file.open("w") as f:
                json.dump(self.items, f, indent=2)
            self.logger.info("Generated file %s", str(output_file))

    def build_item(self, packet, item):
        utc = cuc_to_utc(packet.pus_header.sc_time)
        return {
            "event": self.__class__.__name__,
            "timestamp": utc,
            "data": item
        }

    def calculate_metadata(self):
        pass


class NullProcessor(Processor):
    
    def process(self, packet):
        pass