"""Update the meta-model, the golden test data and verify it for a given version."""

import argparse
import os
import pathlib
import shutil
import subprocess
import sys


def main() -> int:
    """Execute the main routine."""
    this_dir = pathlib.Path(os.path.realpath(__file__)).parent
    repo_root = this_dir.parent.parent

    default_meta_model_version = "3.1"

    default_sdk_path = repo_root.parent / f"aas-core{default_meta_model_version}-python"

    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument(
        "--meta_model_version",
        help="Version of the meta-model which we want to update",
        default=default_meta_model_version,
    )
    parser.add_argument(
        "--sdk_path",
        help="Path to the SDK used to verify the test data",
        default=os.path.relpath(str(default_sdk_path), os.getcwd()),
    )
    args = parser.parse_args()

    meta_model_version = str(args.meta_model_version)
    sdk_path = pathlib.Path(args.sdk_path)

    print("Downloading the latest meta-model...")
    subprocess.check_call(
        [
            sys.executable,
            str(this_dir / "download_latest_aas_core_meta.py"),
            "--meta_model_version",
            meta_model_version,
        ]
    )

    meta_model_version_in_paths = meta_model_version.replace(".", "_")
    golden_dir = (
        repo_root
        / "dev"
        / "test_data"
        / "test_generation"
        / f"v{meta_model_version_in_paths}"
    )

    if golden_dir.exists():
        print(f"Deleting {golden_dir} to re-create it...")
        shutil.rmtree(golden_dir)

    golden_dir.mkdir(parents=True)

    meta_model_path = (
        repo_root
        / "dev"
        / "test_data"
        / "meta_model"
        / f"v{meta_model_version_in_paths}.py"
    )

    print(
        f"Generating the new golden test data "
        f"based on {meta_model_path} to {golden_dir}..."
    )
    subprocess.check_call(
        [
            sys.executable,
            "-m",
            "aas_core_testdatagen",
            "--meta_model_path",
            str(meta_model_path),
            "--output_dir",
            str(golden_dir),
            "--cache_meta_model",
        ]
    )

    print(f"Verifying the data in {golden_dir} with the SDK from {sdk_path} ...")

    subprocess.check_call(
        [
            sys.executable,
            str(this_dir / "verify_test_data_with_sdk.py"),
            "--sdk_path",
            str(sdk_path),
            "--test_data_dir",
            str(golden_dir),
            "--meta_model_path",
            str(meta_model_path),
            "--cache_meta_model",
        ]
    )

    print("Done.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
