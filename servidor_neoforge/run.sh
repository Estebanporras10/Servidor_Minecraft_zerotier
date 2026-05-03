#!/bin/bash
# NeoForge server launcher for Linux/Mac

# Run the server with NeoForge loader
java @user_jvm_args.txt @libraries/net/neoforged/neoforge/21.1.227/unix_args.txt "$@"
