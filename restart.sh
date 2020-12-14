#!/bin/bash

rm webapp/input/*
rm webapp/output/*

flask run --host=0.0.0.0
