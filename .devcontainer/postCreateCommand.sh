#!/usr/bin/env bash

export UV_LINK_MODE=copy;

sudo apt update
sudo apt full-upgrade -y
sudo apt autoremove -y;

sudo apt install -y ruby-foreman;
npm install --save-dev prettier prettier-plugin-jinja-template markdownlint-cli2;

# Install ohmyposh
curl -s https://ohmyposh.dev/install.sh | bash -s

if ! command -v oh-my-posh &> /dev/null; then
    echo "Failed to install oh-my-posh. Please check the installation script."
else
    echo "oh-my-posh installed successfully."
    echo "Setting up oh-my-posh theme..."
    # Install fonts using proper bash array syntax
    fonts=("Hack" "AnonymousPro" "Noto")
    for font in "${fonts[@]}"; do
        oh-my-posh font install "$font"
    done
fi

# Setup shell completions
echo "Setting up shell completions..."

# if uv, uvx, ruff, or oh-my-posh are not available, don't add shell completions for that tool
if ! command -v uv &> /dev/null; then
  echo "uv not found, skipping shell completion setup for uv"
else
  echo "uv found, setting up shell completion"
  uv generate-shell-completion bash > ~/.cache/uv-completion.bash
fi

if ! command -v uvx &> /dev/null; then
  echo "uvx not found, skipping shell completion setup for uvx"
else
  echo "uvx found, setting up shell completion"
  uvx --generate-shell-completion bash > ~/.cache/uvx-completion.bash
fi

if ! command -v ruff &> /dev/null; then
  echo "ruff not found, skipping shell completion setup for ruff"
else
  echo "ruff found, setting up shell completion"
  ruff generate-shell-completion bash > ~/.cache/ruff-completion.bash
fi

if ! command -v oh-my-posh &> /dev/null; then
  echo "oh-my-posh not found, skipping shell completion setup for oh-my-posh"
else
  echo "oh-my-posh found, setting up shell completion"
  oh-my-posh init bash --config ~/.cache/oh-my-posh/themes/paradox.omp.json > ~/.cache/oh-my-posh-completion.bash
fi

# Check if ~/.bashrc already contains the completion setup
if ! grep -q 'uv generate-shell-completion' ~/.bashrc; then
  echo "Adding shell completions to ~/.bashrc"
  cat << EOF >> ~/.bashrc

# Shell completions
if [ -f ~/.cache/uv-completion.bash ]; then
  source ~/.cache/uv-completion.bash
fi
if [ -f ~/.cache/uvx-completion.bash ]; then
  source ~/.cache/uvx-completion.bash
fi
if [ -f ~/.cache/ruff-completion.bash ]; then
  source ~/.cache/ruff-completion.bash
fi
if [ -f ~/.cache/oh-my-posh-completion.bash ]; then
  source ~/.cache/oh-my-posh-completion.bash
fi

export UV_LINK_MODE=copy;

EOF
  echo "Shell completions added to ~/.bashrc"
else
  echo "Shell completions already present in ~/.bashrc"
fi

uv python install
uv pip install -Ur pyproject.toml --group dev

redis-server --daemonize yes;
