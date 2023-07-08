#!/bin/bash
python /app/db_healthcheck.py && alembic upgrade head
