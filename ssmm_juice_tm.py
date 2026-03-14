import argparse
import logging
from pathlib import Path

from kaitai import version
from kaitai.juice_ccsds import JuiceCcsds
from tm_processor.spice.time_utils import setup_spice
from tm_processor.spice.mk_utils import extract_lsk_sclk
import hashlib

from ssmm_processors import (NullProcessor, 
    DirectorySetupProcessor, DirectoryDownlinkProcessor, FileStatusProcessor, 
    RealTimeDownlinkProcessor)
from ssmm_processors.utils import cuc_to_utc, get_packet_description

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)


parser = argparse.ArgumentParser(
    description="Process the JUICE SSMM telemetry packets",
)

parser.add_argument("-v","--version", action="version", version=f"JUICE CCSDS processor {version}")
parser.add_argument("-f", "--file", type=str, help="Juice CCSDS file", required=True)
parser.add_argument("-m", "--metakernel", type=Path, help="Path to spice kernels", default="/Users/randres/git/spice/juice/kernels/mk/juice_ops_local.tm")
parser.add_argument("-d", "--debug", action="store_true", help="Enable debug logging")



payload = {
    JuiceCcsds.DirectorySetup: DirectorySetupProcessor,
    JuiceCcsds.DirectoryDownlink: DirectoryDownlinkProcessor,
    JuiceCcsds.FileStatus: FileStatusProcessor,
    JuiceCcsds.RealTimeDownlink: RealTimeDownlinkProcessor,
    JuiceCcsds.UnknowPayload: NullProcessor,
}


def main():
    args = parser.parse_args()
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO if not args.debug else logging.DEBUG)

    lsk,  sclk, mk_id = extract_lsk_sclk(args.metakernel, 'juice')

    logger.info(f"LSK: {lsk}")
    logger.info(f"SCLK: {sclk}")
    logger.debug(f"MK_ID: {mk_id}")

    setup_spice(lsk, sclk)

    processor = None

    try:
        bundle = JuiceCcsds.from_file(args.file)
        processed = set()
        for packet in bundle.packets:
            pus_header = packet.pus_header
            md5 = hashlib.md5(packet._raw_payload).hexdigest()
            if md5 in processed:
                logger.debug("Duplicated packet")
                continue
            processed.add(md5)
            utc = cuc_to_utc(pus_header.sc_time)
            logger.info("%s - %s", utc, get_packet_description(packet))
            
            if processor is None:
                packet_class = type(packet.payload)
                processor = payload[type(packet.payload)](args.file, packet_class)

            processor.process(packet)

        processor.dump()

    except Exception as e:
        print(f"process_tm.py: error: {e}")
        return 1

if __name__ == "__main__":
    main()
