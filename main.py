import argparse
import os
import zipfile
import pwd
import grp
from datetime import datetime, timedelta


def is_dry_run():
    """Check if the script is running in dry run mode."""
    return os.getenv("DRY_RUN", False) == "true"


def is_folder_empty(folder_path):
    """
    Check if a folder is empty (no files or subdirectories).
    """
    # os.listdir() returns a list of entries in the folder
    return not os.listdir(folder_path)


def get_uid(user_name):
    """Get the UID for a given username."""
    try:
        return int(user_name)
    except ValueError:
        try:
            uid = pwd.getpwnam(user_name).pw_uid
            return uid
        except KeyError:
            return None


def get_gid(group_name):
    """Get the GID for a given group name."""
    try:
        return int(group_name)
    except ValueError:
        try:
            gid = grp.getgrnam(group_name).gr_gid
            return gid
        except KeyError:
            return None


def humanize_bytes(bytes, precision=2):
    """Return a humanized string representation of a number of bytes."""
    abbrevs = (
        (1 << 50, "PB"),
        (1 << 40, "TB"),
        (1 << 30, "GB"),
        (1 << 20, "MB"),
        (1 << 10, "kB"),
        (1, "bytes"),
    )
    if bytes == 1:
        return "1 byte"
    for factor, suffix in abbrevs:
        if bytes >= factor:
            break
    return f"{bytes / factor:.{precision}f} {suffix}"


def adjust_file_retention(folder_path, keep_n_files=None, keep_n_days=None):
    """
    Adjust the number of files in a folder by deleting the oldest files.
    :param folder_path:
    :param keep_n_files:
    :param keep_n_days:
    :return:
    """
    if is_dry_run():
        print(f"Adjusting file retention for {folder_path}...")
        print(f"keep_n_files: {keep_n_files}")
        print(f"keep_n_days: {keep_n_days}")

    files_to_delete = []
    files = sorted(
        os.listdir(folder_path),
        key=lambda x: os.path.getmtime(os.path.join(folder_path, x)),
    )

    # validate the last and first file is sorted correctly otherwise reverse the list
    if files and os.path.getmtime(
        os.path.join(folder_path, files[0])
    ) > os.path.getmtime(os.path.join(folder_path, files[-1])):
        files = files[::-1]

    if keep_n_files is not None:
        files_to_keep = files[-keep_n_files:]

        # Removes files to keep from files
        for f in files_to_keep:
            files.remove(f)

        files_to_delete = files

    if keep_n_days is not None:
        # Delete files older than y days
        cutoff_date = datetime.now() - timedelta(days=keep_n_days)
        files_to_delete = [
            f
            for f in files
            if datetime.fromtimestamp(os.path.getmtime(os.path.join(folder_path, f)))
            < cutoff_date
        ]

    # Example deletion logic
    for f in files_to_delete:
        # if env DRY_RUN is true
        if is_dry_run():
            print(f"Would delete {f}")
            continue
        else:
            os.remove(os.path.join(folder_path, f))
            print(f"Deleted {f}")


def zip_folder(
    source,
    destination,
    owner,
    group,
    keep_n_days,
    keep_n_files,
    timestamp_format="%Y%m%d_%H%M%S",
):
    """
    Zips the input folder and saves it to the output folder with a timestamp.
    Optionally, set the owner of the output zip file.
    """

    print(f"Zipping folder {source} to {destination}...")
    if not os.path.isdir(source):
        raise ValueError("Input folder does not exist or is not a directory.")

    # Check if the folder is empty
    if is_folder_empty(source):
        print("The input folder is empty. No zip file created.")
        return  # Exit the function if the folder is empty

    # Ensuring the output folder exists
    if not os.path.exists(destination):
        os.makedirs(destination)

    # Creating the zip file name with a timestamp
    timestamp = datetime.now().strftime(timestamp_format)
    base_name = os.path.basename(os.path.normpath(source))
    zip_filename = f"{base_name}_{timestamp}.zip"
    zip_filepath = os.path.join(destination, zip_filename)

    # Creating the zip archive
    with zipfile.ZipFile(zip_filepath, "w", zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(source):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, start=source)
                zipf.write(file_path, arcname)
    # get the size of zip
    size = os.path.getsize(zip_filepath)
    # humanize the size

    print(
        f"Folder {source} zipped successfully to {zip_filepath} ({humanize_bytes(size)})"
    )
    os.chown(zip_filepath, owner, group)

    # Delete old files
    adjust_file_retention(destination, keep_n_files, keep_n_days)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Zip an input folder and output it with a timestamp."
    )
    parser.add_argument(
        "--source",
        type=str,
        default=os.getenv("INPUT_FOLDER"),
        help="The input folder to zip.",
    )
    parser.add_argument(
        "--destination",
        type=str,
        default=os.getenv("OUTPUT_FOLDER"),
        help="The output folder where the zip file will be saved.",
    )
    parser.add_argument(
        "--user",
        type=str,
        default=os.getenv("OUTPUT_USER", "root"),
        help='The user or group to own the zip file. Defaults to "root".',
    )
    parser.add_argument(
        "--group",
        type=str,
        default=os.getenv("OUTPUT_GROUP", "root"),
        help='The user or group to own the zip file. Defaults to "root".',
    )
    parser.add_argument(
        "--keep-n-days",
        type=int,
        default=os.getenv("KEEP_N_DAYS", 0),
        help="The number of days to keep the zip file. Defaults to 0 (no limit).",
    )
    parser.add_argument(
        "--keep-n-files",
        type=int,
        default=os.getenv("KEEP_N_FILES", 0),
        help="The number of files to keep. Defaults to 0 (no limit).",
    )

    args = parser.parse_args()

    print(args)

    args.owner = get_uid(args.user) or 0
    args.group = get_gid(args.group) or 0
    # remove user from args
    del args.user

    # Example: For cron scheduling, you would handle it outside this script
    # supply args from argparse but also inject user and group
    zip_folder(**vars(args))
