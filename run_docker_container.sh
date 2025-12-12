# before, do this on local machine to set your wandb api key
# export WANDB_API_KEY=your_wandb_api_key_here
# export HF_TOKEN=your_huggingface_token_here

docker run --rm --gpus all -it --network host \
  --ipc=host \
  -v "$PWD:/workspace" \
  -v "$HOME/.cache/huggingface:/root/.cache/huggingface" \
  -v "$HOME/.cache/wandb:/root/.cache/wandb" \
  -e HF_HOME=/root/.cache/huggingface \
  -e WANDB_DIR=/root/.cache/wandb \
  -e WANDB_API_KEY="$WANDB_API_KEY" \
  -e HF_TOKEN="$HF_TOKEN" \
  -e HUGGINGFACE_HUB_TOKEN="$HF_TOKEN" \
  lerobot-cu128 bash

# or then 
# wandb login
# huggingface-cli login
# request access to google/paligemma-3b-pt-224 on HF