#!/bin/bash
cd "$(dirname "$0")"; export WS_USERS="${WS_USERS:-admin:admin}"; python3 app.py
