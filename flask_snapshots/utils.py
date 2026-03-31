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


    return added_files, removed_files