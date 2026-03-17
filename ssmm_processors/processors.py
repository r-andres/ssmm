from datetime import datetime
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


    def dump(self, output_folder: Path, split: bool = False):
        if split:
            self.dump_split(output_folder)
        else:
            self.dump_unique(output_folder)

    def dump_unique(self, output_folder: Path):
        if len(self.items) > 0:
            self.calculate_metadata()
            output_file = output_folder / Path(self.file).with_suffix(f".{self.packet_class.__name__}.json").name
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

    def dump_split(self, output_folder: Path):
        if len(self.items) > 0:
            self.calculate_metadata()
            for item in self.items:
                timestamp = item.get("timestamp")
                date = datetime.fromisoformat(timestamp.replace("Z", ""))
                parent_folder = self.get_timed_folder(output_folder, date)
                output_file =  parent_folder /f"{self.packet_class.__name__}_{self.get_file_timestamp(date)}.json"
                with output_file.open("w") as f:
                    json.dump(item, f, indent=2)
                self.logger.info("Generated file %s", str(output_file))

    def get_timed_folder(self, output_folder: Path, date: datetime):
        timed_folder = output_folder / f"{date.year}{date.month:02d}/{date.day}"
        timed_folder.mkdir(parents=True, exist_ok=True)
        return timed_folder
    
    def get_file_timestamp(self, date: datetime):
        return date.isoformat(timespec="seconds").replace(":", "").replace("-", "").replace("T", "")


class NullProcessor(Processor):
    
    def process(self, packet):
        pass