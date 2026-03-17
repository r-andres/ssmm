def diff_file_structures(old_data, new_data):

    old_dirs = set(old_data.keys())
    new_dirs = set(new_data.keys())

    added_files = []
    removed_files = []

    # Apps present in both → compare files
    for dir in old_dirs & new_dirs:
        old_files = old_data[dir]
        new_files = new_data[dir]
        old_file_ids = set(old_files.keys())
        new_file_ids = set(new_files.keys())

        # Files added/removed
        for fid in new_file_ids - old_file_ids:
            added_files.append([f"{dir}/{fid}", f"{new_files[fid].get('creation_time')}", f"{new_files[fid].get('file_size')}"])

        for fid in old_file_ids - new_file_ids:
            removed_files.append([f"{dir}/{fid}", f"{old_files[fid].get('creation_time')}", f"{old_files[fid].get('file_size')}"])


    return added_files, removed_files