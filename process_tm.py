import argparse
import logging
from pathlib import Path

from kaitai import version
from kaitai.juice_ccsds import JuiceCcsds
from tm_processor.kaitai.time_utils import get_dds_timestamp
from tm_processor.spice.time_utils import get_cuc_time_48_bits, get_sclk_str, setup_spice, scs2utc
from tm_processor.spice.mk_utils import extract_lsk_sclk
import hashlib
import json

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


def rt_processor(payload: JuiceCcsds.RealTimeDownlink):

    SESSION_ACTIVE = 2
    STATE_MAP = {
            0: "INACTIVE",
            1: "SUSPENDED",
            2: "RUNNING"
    }

    if payload.cfdp_ka_session_state != SESSION_ACTIVE and payload.cfdp_x_session_state != SESSION_ACTIVE:
        return None
    item = {}
    if payload.cfdp_ka_session_state == SESSION_ACTIVE:
        item["ka"] = {
             "state": STATE_MAP[payload.cfdp_ka_session_state],
             "open_transactions": payload.cfdp_numberoftrans_ka
         }
        if payload.cfdp_ka_current_file_id != 0:
             item["ka"]["transmitting"] = {
                 "directory_id": payload.cfdp_ka_current_directory_id,
                 "file_id": file_id_hex(payload.cfdp_ka_current_file_id)
             }
    if payload.cfdp_x_session_state == SESSION_ACTIVE:
        item["x"] = {
             "state": STATE_MAP[payload.cfdp_x_session_state],
             "open_transactions": payload.cfdp_numberoftrans_x
         }
        if payload.cfdp_x_current_file_id != 0:
             item["x"]["transmitting"] = {
                 "directory_id": payload.cfdp_x_current_directory_id,
                 "file_id": file_id_hex(payload.cfdp_x_current_file_id)
             }

    return item


def dd_processor(payload: JuiceCcsds.DirectoryDownlink):

    item = {}
    for entry in payload.directories:
        item[entry.directory_id] = {
            "directory_id": entry.directory_id,
            "state":  "ENABLED" if entry.state == 1 else "DISABLED",
            "priority":  entry.priority,
            "rf_band": "x" if entry.rf_band == 0 else "ka"
        }
    return item

def ds_processor(payload: JuiceCcsds.DirectorySetup):

    item = {}
    for entry in payload.directories:
        item[entry.directory_id] = {
            "directory_id": entry.directory_id,
            "max_dir_size": entry.max_dir_size,
            "max_file_size": entry.max_file_size,
            "max_wrt_timeout": entry.max_wrt_timeout,
            "max_wrt_speed": entry.max_wrt_speed
        }
    return item


def fs_processor(payload: JuiceCcsds.FileStatus):

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
            "file_protect_status": entry.file_protect_status,
            "file_mode": entry.file_mode,
            "creation_time_cuc": cuc_to_utc(entry.creation_time_cuc) 
        }
    return item



def null_processor(payload):
    return None

payload = {
    JuiceCcsds.DirectorySetup: ds_processor,
    JuiceCcsds.DirectoryDownlink: dd_processor,
    JuiceCcsds.FileStatus: fs_processor,
    JuiceCcsds.RealTimeDownlink: rt_processor,
    JuiceCcsds.UnknowPayload: null_processor,
}


def cuc_to_utc(cuc):
    cuc_coarse, cuc_fine = get_cuc_time_48_bits(cuc)
    sclk_str = get_sclk_str(cuc_coarse, cuc_fine)
    return scs2utc(JUICE_SC_ID, sclk_str) + 'Z'

def file_id_hex(file_id):
    return f"{file_id:#04x}"

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

    items = []

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
            
            packet_class = type(packet.payload)
            processor = payload[type(packet.payload)]
            item = processor(packet.payload)
            if item:
                items.append({
                    "timestamp": utc,
                    "event": packet_class.__name__,
                    "data": item
                })

        if len(items) > 0:
            output_file = Path(args.file).with_suffix(f".{packet_class.__name__}.json")
            with output_file.open("w") as f:
                json.dump(items, f, indent=2)   

    except Exception as e:
        print(f"process_tm.py: error: {e}")
        return 1

if __name__ == "__main__":
    main()
