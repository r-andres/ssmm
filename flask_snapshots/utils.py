import json

def diff_file_structures(downlink_state, old_data, new_data):

    old_dirs = set(old_data.keys())
    new_dirs = set(new_data.keys())

    added_files = []
    removed_files = []

    # Apps present in both → compare files
    for dir in old_dirs & new_dirs:
        dir_state = 'UNKNOWN'
        if downlink_state is not None:
            dir_state = downlink_state.get(dir, {"state": "UNKOWN"}).get("state")

        old_files = old_data[dir]
        new_files = new_data[dir]
        old_file_ids = set(old_files.keys())
        new_file_ids = set(new_files.keys())

        # Files added/removed
        for fid in new_file_ids - old_file_ids:
            added_files.append({ **new_files[fid], 'file_dir': dir, 'dir_dw_state': dir_state})

        for fid in old_file_ids - new_file_ids:
            removed_files.append({ **old_files[fid], 'file_dir': dir, 'dir_dw_state': dir_state })

    # 2. Entire new directories → all files are "added"
    for dir in new_dirs - old_dirs:
        dir_state = 'UNKNOWN'
        if downlink_state is not None:
            dir_state = downlink_state.get(dir, {"state": "UNKOWN"}).get("state")

        for fid, file_data in new_data[dir].items():
            added_files.append({**file_data, 'file_dir': dir, 'dir_dw_state': dir_state})

    # 3. Entire removed directories → all files are "removed"
    for dir in old_dirs - new_dirs:
        dir_state = 'UNKNOWN'
        if downlink_state is not None:
            dir_state = downlink_state.get(dir, {"state": "UNKOWN"}).get("state")
        for fid, file_data in old_data[dir].items():
            removed_files.append({**file_data, 'file_dir': dir, 'dir_dw_state': dir_state})


    return added_files, removed_files