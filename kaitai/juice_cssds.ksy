meta:
  id: juice_ccsds
  bit-endian: be
  endian: be

seq:
  - id: packets
    type: packet
    repeat: eos


types:

  packet:
    seq:
      - id: dds
        type: dds_section

      - id: primary_header
        type: ccsds_primary_header

      - id: pus_header
        type: pus_secondary_header

      - id: payload
        size: dds.len_packet_data - 16
        type:
          switch-on: (pus_header.service_type << 8) | pus_header.service_subtype
          cases:
            # ------------------------------------------------------------------
            # Real Time Downlink    SPID 10433    SType: 3      SSubtype: 25
            # ------------------------------------------------------------------
            0x319: real_time_downlink
            # ------------------------------------------------------------------
            # File status:          SPID 10258     SType: 144    SSubtype: 6
            # ------------------------------------------------------------------
            0x9006: file_status
            # ------------------------------------------------------------------
            # Directory downlink    SPID 10428     SType: 159    SSubtype: 17
            # ------------------------------------------------------------------
            0x9f11: directory_downlink
            # ------------------------------------------------------------------
            # Directory setup      SPID 10265      SType: 170    SSubtype: 27
            # ------------------------------------------------------------------
            0xAA1B: directory_setup
            _: unknow_payload


  dds_section:
    seq:
      - id: seconds
        type: u4
      - id: microseconds
        type: u4
      - id: len_packet_data
        type: u4
      - id: ground_station
        type: u2
      - id: virtual_channel
        type: u2
      - id: sle_type
        type: u1
      - id: time_quality
        type: u1


  ccsds_primary_header:
    seq:
      - id: version_number
        type: b3
      - id: packet_type
        type: b1
      - id: secondary_header_flag
        type: b1
      - id: apid
        type: b11
      - id: sequence_flags
        type: b2
      - id: sequence_counter
        type: b14
      - id: packet_length
        type: u2


  pus_secondary_header:
    seq:
      - id: spare
        type: b1
      - id: pus_version
        type: b3
      - id: spare2
        type: b4
      - id: service_type
        type: u1
      - id: service_subtype
        type: u1
      - id: destination
        type: u1
      - id: sc_time
        size: 6


#-------------------------------------------------------------------------------
#
# Directory setup      SPID 10265      SType: 170    SSubtype: 27 
#
#-------------------------------------------------------------------------------

  directory_setup:
    seq:
      - id: partition_id
        type: u1
      - id: num_directories
        type: u4
      - id: directories
        type: directory_setup_entry
        repeat: expr
        repeat-expr: num_directories


  directory_setup_entry:
    seq:
      - id: directory_id
        type: str
        encoding: ASCII
        size: 4
      - id: max_dir_size
        type: u4
      - id: max_file_size
        type: u4
      - id: max_wrt_timeout
        type: u4
      - id: max_wrt_speed
        type: u4

#-------------------------------------------------------------------------------
#
# File status:          SPID 10258     SType: 144    SSubtype: 6
#
#-------------------------------------------------------------------------------


  file_status:
    seq:

      - id: partition_id
        size: 1
      - id: num_files
        type: u2be
      - id: files
        type: file
        repeat: expr
        repeat-expr: num_files  
        
  file:
    seq:
      - id: directory_id
        type: str
        size: 4
        encoding: ASCII
      - id: file_id
        type: u4be
      - id: file_address
        type: u4be
      - id: file_size
        type: u4be
      - id: file_type
        type: u4be
      - id: file_protect_status
        type: u4be
      - id: file_mode
        type: u4be
      - id: creation_time_cuc
        size: 6

#-------------------------------------------------------------------------------
#
# Directory downlink    SPID 10428     SType: 159    SSubtype: 17
#
#-------------------------------------------------------------------------------


  directory_downlink:
    seq:
      - id: num_directories
        type: u4be
      - id: directories
        type: directory_downlink_entry
        repeat: expr
        repeat-expr: num_directories  
        
  directory_downlink_entry:
    seq:
      - id: partition
        size: 1
      - id: directory_id
        type: str
        size: 4
        encoding: ASCII
      - id: state
        type: u1
      - id: priority
        type: u1
      - id: rf_band
        type: u1

#-------------------------------------------------------------------------------
#
# Real Time Downlink    SPID 10433    SType: 3      SSubtype: 25
#
#-------------------------------------------------------------------------------


  real_time_downlink:
    seq:
        - id: hk_structure_id
          type: u4
        - id: ldt_reception_timeout
          type: u4
        - id: ft1_numberexpectedsdu
          type: u4
        - id: ft1_ldu_id
          type: u4
        - id: ft1_numberreceivedsdu
          type: u4
        - id: ft1_uplink_state
          size: 4
        - id: ft2_numberexpectedsdu
          type: u4
        - id: ft2_ldu_id
          type: u4
        - id: ft2_numberreceivedsdu
          type: u4
        - id: ft2_uplink_state
          size: 4
        - id: cfdp_ka_downlink_rate
          type: u4
        - id: cfdp_ka_session_state
          type: u1
        - id: cfdp_ka_current_directory_id
          size: 4
          type: str
          encoding: ASCII
        - id: cfdp_ka_current_file_id
          type: u4
        - id: cfdp_numberoftrans_ka
          type: u4
        - id: cfdp_x_downlink_rate
          type: u4
        - id: cfdp_x_session_state
          type: u1
        - id: cfdp_x_current_directory_id
          size: 4
          type: str
          encoding: ASCII
        - id: cfdp_x_current_file_id
          type: u4
        - id: cfdp_numberoftrans_x
          type: u4

  unknow_payload:
    seq:
      - id: data
        size-eos: true