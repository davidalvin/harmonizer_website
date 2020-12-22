#!/bin/bash

# CLEAR INPUT AND OUTPUT DIRECTORIES
clear
rm webapp/input/*
rm webapp/output/*

# CHANGE THIS BEFORE RUNNING ON PRODUCTION
export FLASK_ENV=development

python run.py
