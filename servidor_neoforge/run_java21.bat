@echo off
REM NeoForge server launcher for Java 21 explicitly

java -version 21 @user_jvm_args.txt @libraries/net/neoforged/neoforge/21.1.227/win_args.txt %*
pause
