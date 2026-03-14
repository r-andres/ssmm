from pathlib import Path
import json
import logging


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
            output_file = Path(self.file).with_suffix(f".{self.packet_class.__name__}.json")
            with output_file.open("w") as f:
                json.dump(self.items, f, indent=2)
            self.logger.info("Generated file %s", str(output_file))


class NullProcessor(Processor):
    
    def process(self, packet):
        pass