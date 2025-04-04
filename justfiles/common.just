# REQUIRES

# docker := require("docker")
find := require("find")
rm := require("rm")
uv := require("uv")

# SETTINGS

# Load a .env file, if present.
set dotenv-load := true

set shell := ["zsh", "-cu"]
