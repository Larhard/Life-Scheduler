import subprocess


def get_revision_hash():
    try:
        result = subprocess.check_output(["/usr/bin/git", "rev-parse", "HEAD"])
        result = result.decode()
        result = result.strip()
        return result
    except (FileNotFoundError, subprocess.CalledProcessError):
        return None
