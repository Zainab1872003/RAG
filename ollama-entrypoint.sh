#!/bin/sh
set -e

# Start the Ollama server in the background
ollama serve &

# Wait a few seconds for the server to be ready
sleep 3

# Pull the mistral model
ollama pull mistral

# Wait for the background server process to finish
wait
