# Property Monitor

This repository contains a simple Python script to monitor rental listings on
[Funda](https://www.funda.nl) and [Pararius](https://www.pararius.nl). It checks
for houses available for rent in **Delft** and **Delfgauw** with at least three
rooms and a maximum price of €2750.

The script runs in a loop every 30 minutes and prints new listings to the
console. It remembers previously seen listings in `listings.json` so that you
are only notified when something new appears.

## Requirements

The script is implemented using only the Python standard library. No external
packages are required.

## Running

```bash
python3 property_monitor.py
```

Because the Codex execution environment blocks network access, the script cannot
be executed here. When run in a normal environment with internet access, it will
fetch the search pages from Funda and Pararius every 30 minutes and display any
newly found listings.
