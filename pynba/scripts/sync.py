"""Script to sync data directory to s3"""

import logging
import subprocess

from pynba.config import config


logger = logging.getLogger(__name__)


def main():
    """Syncs local data directory to s3"""
    source = config.local_data_directory
    dest = f"s3://{config.aws_s3_bucket}/{config.aws_s3_key_prefix}"
    logger.info(f"Syncing local data directory {source} to {dest}")
    subprocess.run(
        ["aws", "s3", "sync", source, dest, "--exclude", "*.gitignore"],
        check=True,
    )
    logger.info("Sync complete!")


if __name__ == "__main__":
    main()
