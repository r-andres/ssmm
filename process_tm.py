import argparse
import logging
from pathlib import Path

from kaitai import version
from kaitai.juice_ccsds import JuiceCcsds
from tm_processor.kaitai.time_utils import get_dds_timestamp
from tm_processor.spice.time_utils import get_cuc_time_48_bits, get_sclk_str, setup_spice, scs2utc
from tm_processor.spice.mk_utils import extract_lsk_sclk
import hashlib

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)


parser = argparse.ArgumentParser(
    description="Process the JUICE tm packet",
)

parser.add_argument("-v","--version", action="version", version=f"JUICE CCSDS processor {version}")
parser.add_argument("-f", "--file", type=str, help="Juice CCSDS file", required=True)
parser.add_argument("-m", "--metakernel", type=Path, help="Path to spice kernels", default="/Users/randres/git/spice/juice/kernels/mk/juice_ops_local.tm")
parser.add_argument("-d", "--debug", action="store_true", help="Enable debug logging")



payload = {
    JuiceCcsds.DirectorySetup: "DirectorySetup",
    JuiceCcsds.DirectoryDownlink: "DirectoryDownlink",
    JuiceCcsds.FileStatus: "FileStatus",
    JuiceCcsds.RealTimeDownlink: "RealTimeDownlink",
    JuiceCcsds.UnknowPayload: "UnknowPayload",
}


def get_service_code(packet):
    return (packet.pus_header.service_type << 8) | packet.pus_header.service_subtype

def get_packet_description(packet):
    return f"""
  Apid: {packet.primary_header.apid}
  Sequence Counter: {packet.primary_header.sequence_counter}
  Service Type: {packet.pus_header.service_type}
  Service Subtype: {packet.pus_header.service_subtype}
  ID: {get_service_code(packet):#04x}
"""

JUICE_SC_ID = -28

def main():
    args = parser.parse_args()
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO if not args.debug else logging.DEBUG)

    lsk,  sclk, mk_id = extract_lsk_sclk(args.metakernel, 'juice')

    logger.info(f"LSK: {lsk}")
    logger.info(f"SCLK: {sclk}")
    logger.debug(f"MK_ID: {mk_id}")

    setup_spice(lsk, sclk)

    try:
        bundle = JuiceCcsds.from_file(args.file)
        processed = set()
        for packet in bundle.packets:
            pus_header = packet.pus_header
            dds = packet.dds
            md5 = hashlib.md5(packet._raw_payload).hexdigest()
            if md5 in processed:
                logger.debug("Duplicated packet")
                continue
            processed.add(md5)

            # logger.info(get_dds_timestamp(dds.seconds, dds.microseconds))
            cuc_coarse, cuc_fine = get_cuc_time_48_bits(pus_header.sc_time)
            sclk_str = get_sclk_str(cuc_coarse, cuc_fine)
            utc = scs2utc(JUICE_SC_ID, sclk_str)
            logger.info("%s - %s", utc, get_packet_description(packet))
            logger.info(f"Payload: {payload[type(packet.payload)]}")
            logger.info(f"MD5: {md5}")
            logger.info(f"Payload size: {packet.payload._io.size()} bytes {dds.len_packet_data - 16} bytes")


    except Exception as e:
        print(f"process_tm.py: error: {e}")
        return 1

if __name__ == "__main__":
    main()
