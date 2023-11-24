#! /usr/bin/env bash

export PYTHONPATH=$PWD

# Initialize database
python initials/db_starter.py

# Run migrations
alembic upgrade heads

# Create initial data
python initials/initial_data.py