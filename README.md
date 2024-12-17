# Packer tool

## Description

Combined functionality of the scraper tool and the shipper tool.

## Major changes

- Obviously the main change that the scraper and the shipper are in one program.
- New user interface, changing to a web app that allows for easier development.

## Update log

### 4th October 2024 - v0

- Started planning the project and what needs to be done, pulled my shipper into the project to pull functions from.
- Need the scraper from Ed to begin looking at the functions in there.
- Need to plan out all basic functionality properly and meet with Webby to see what functionality he wants.

### 29-11-2024 - v1.5

- Have begun development and successfully implemented:
  - Pulling orders from Odoo
  - Fedex Quoting
  - UPS Quoting
- Project versioning is a bit chaotic as I am solo developing this (the other collaborator is my personal GitHub)
- I will try to update this log as development continues as I have been making large progress with few commits and no updates to this log. (Each Minor update I will update this)

### 10-12-2024 - v1.7

- Forgot to update this in 1.6 but mainly just finished implementing UPS and FEDEX quoting + shipping
- Added logging for debugging

### 10-12-2024 - v1.8

- Added ability to report an issue with clickup from the application

### 10-12-2024 - v1.9

- Added ability to change the currently selected shipper

### 17-12-2024 - v1.12

- Missed a few version updates but have an almost fully functional shipper system now with label printing etc
