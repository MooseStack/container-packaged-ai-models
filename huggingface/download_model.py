import os
from huggingface_hub import snapshot_download

def main():
    repo_id = os.getenv("HUGGINGFACE_MODEL_REPO")
    print(f"Downloading model from Hugging Face repository: {repo_id}")
    if not repo_id:
        raise EnvironmentError("HUGGINGFACE_MODEL_REPO environment variable is not set.")

    snapshot_download(
        repo_id=repo_id,
        local_dir="/models",
        allow_patterns=["*"],
    )

if __name__ == "__main__":
    main()
