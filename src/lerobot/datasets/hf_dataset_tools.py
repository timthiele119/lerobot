from dotenv import load_dotenv
load_dotenv()

import os
import json
import subprocess

from huggingface_hub import HfApi
from huggingface_hub.utils import HfHubHTTPError


REPO_W_MULTIPLE_RECORDING_BATCHES = "/Users/timthiele/Documents/MA/Data/dual_cam/vanilla_pick_and_drop"
HF_USER_OR_ORG = "timt119"
HF_DATASET_PREFIX = "vanilla_pick_and_drop"


def ensure_version_tag(api: HfApi, repo_id: str, codebase_version: str) -> None:
    """
    Create the LeRobot 'codebase version' tag if needed.
    - Skip invalid tags like 'main' (branch name).
    - Ignore 409 conflicts (tag already exists).
    """
    if not codebase_version:
        raise ValueError(f"{repo_id}: missing codebase_version")

    if codebase_version.strip().lower() == "main":
        print(f"[WARN] {repo_id}: codebase_version='main' (branch). Skipping tag creation.")
        return

    try:
        api.create_tag(repo_id, tag=codebase_version, repo_type="dataset")
        print(f"[OK] Tagged {repo_id} with {codebase_version}")
    except HfHubHTTPError as e:
        status = getattr(e.response, "status_code", None)
        if status == 409 and "Tag reference exists already" in str(e):
            print(f"[OK] Tag already exists for {repo_id}: {codebase_version}")
            return
        raise


def main():
    api = HfApi(token=os.environ["HF_TOKEN"])

    sub_datasets = [
        os.path.join(REPO_W_MULTIPLE_RECORDING_BATCHES, d)
        for d in os.listdir(REPO_W_MULTIPLE_RECORDING_BATCHES)
        if os.path.isdir(os.path.join(REPO_W_MULTIPLE_RECORDING_BATCHES, d))
    ]

    repo_ids = []
    for sub_dataset_path in sub_datasets:
        batch_name = os.path.basename(sub_dataset_path.rstrip("/"))
        repo_id = f"{HF_USER_OR_ORG}/{HF_DATASET_PREFIX}_{batch_name}"
        repo_ids.append(repo_id)

        # 1) Ensure repo exists (dataset repo)
        api.create_repo(repo_id, repo_type="dataset", exist_ok=True)

        # 2) Upload folder contents (even if repo already existed)
        api.upload_folder(
            repo_id=repo_id,
            folder_path=sub_dataset_path,
            repo_type="dataset",
            path_in_repo=".",   # upload to repo root
            commit_message=f"Upload {batch_name}",
        )

        # 3) Read local meta/info.json to get codebase_version and tag the repo
        info_path = os.path.join(sub_dataset_path, "meta", "info.json")
        if not os.path.exists(info_path):
            raise FileNotFoundError(
                f"{info_path} not found. This subdir is not a LeRobot dataset (missing meta/info.json)."
            )

        with open(info_path, "r") as f:
            codebase_version = json.load(f).get("codebase_version")

        ensure_version_tag(api, repo_id, codebase_version)

    # Merge + push
    merged_repo_id = f"{HF_USER_OR_ORG}/{HF_DATASET_PREFIX}_merged"
    repo_ids_arg = repr(repo_ids)  # LeRobot expects a python-list-like string

    merge_cmd = [
        "lerobot-edit-dataset",
        "--repo_id", merged_repo_id,
        "--operation.type", "merge",
        "--operation.repo_ids", repo_ids_arg,
        "--push_to_hub", "true",
    ]
    print("Running merge command:", " ".join(merge_cmd))
    subprocess.run(merge_cmd, check=True)


if __name__ == "__main__":
    main()