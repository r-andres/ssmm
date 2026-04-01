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
            added_files.append({ **new_files[fid], 'file_dir': dir })

        for fid in old_file_ids - new_file_ids:
            removed_files.append({ **old_files[fid], 'file_dir': dir })

    # 2. Entire new directories → all files are "added"
    for dir in new_dirs - old_dirs:
        for fid, file_data in new_data[dir].items():
            added_files.append({**file_data, 'file_dir': dir})

    # 3. Entire removed directories → all files are "removed"
    for dir in old_dirs - new_dirs:
        for fid, file_data in old_data[dir].items():
            removed_files.append({**file_data, 'file_dir': dir})


    return added_files, removed_files