import modal

MODEL_NAME = "NousResearch/Hermes-3-Llama-3.1-70B-FP8"
MODEL_REVISION = "091814e7b637c90d9bb62aee6eddfa38b22cd5da"

volume = modal.Volume.from_name("llamas", create_if_missing=True)
volumes = {"/llamas": volume}

image = (
    modal.Image.debian_slim(python_version="3.10")
    .pip_install(
        [
            "vllm==0.5.3post1",  # LLM serving
            "huggingface_hub",  # download models from the Hugging Face Hub
            "hf-transfer",  # download models faster
        ]
    )
    .env({"HF_HUB_ENABLE_HF_TRANSFER": "1"})
)


MINUTES = 60
HOURS = 60 * MINUTES


app = modal.App(image=image, secrets=[modal.Secret.from_name("huggingface")])


# should take about 30 minutes
@app.function(volumes=volumes, timeout=4 * HOURS)
def download_model(model_dir, model_name, model_revision):
    import os

    from huggingface_hub import snapshot_download

    volume.reload()
    os.makedirs(model_dir, exist_ok=True)

    snapshot_download(
        model_name,
        local_dir=model_dir,
        ignore_patterns=["*.pt", "*.bin", "*.pth", "original/*"],  # Ensure safetensors
        revision=model_revision,
    )

    volume.commit()


@app.local_entrypoint()
def main(model_name: str = None, model_revision: str = None):
    MODEL_DIR = f"/llamas/{MODEL_NAME}"
    if model_name is None:
        model_name = MODEL_NAME
        model_revision = MODEL_REVISION
    download_model.remote(MODEL_DIR, model_name, model_revision)
