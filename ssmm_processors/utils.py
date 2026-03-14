
from tm_processor.spice.time_utils import get_cuc_time_48_bits, get_sclk_str, scs2utc


JUICE_SC_ID = -28

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