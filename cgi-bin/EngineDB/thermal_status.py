#!./cgi_runner.sh

import numpy as np
import sys
import json
import requests
import html
from datetime import datetime
from zoneinfo import ZoneInfo

# CGI header
print("Content-Type: text/html; charset=utf-8\n")


data=requests.get("http://zcu102b:8897").json()


current = max(data, key=lambda x: x["timestamp"])
current_state = current["new_state"]




CENTRAL = ZoneInfo("America/Chicago")

def format_ts(ts):
    dt = datetime.fromtimestamp(ts, tz=CENTRAL)
    return dt.strftime("%Y-%m-%d %H:%M:%S %Z")

print("""
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>State Transitions</title>
   <style>
    body {
      font-family: system-ui, sans-serif;
      margin: 2em;
    }
    .status {
      padding: 1.2em;
      margin-bottom: 2em;
      border-radius: 8px;
      font-size: 1.8em;
      font-weight: bold;
      text-align: center;
    }
    .OFF { background: #fdecea; color: #b00020; }
    .SETUP { background: #fff4e5; color: #f57c00; }
    .RUNNING { background: #e8f5e9; color: #2e7d32; }

    table {
      border-collapse: collapse;
      width: 100%;
    }
    th, td {
      border: 1px solid #ccc;
      padding: 0.5em 0.7em;
      text-align: left;
      vertical-align: top;
    }
    th {
      background: #f5f5f5;
    }
    tr:nth-child(even) {
      background: #fafafa;
    }
    .state {
      font-weight: bold;
    }
    .duration {
      text-align: right;
      white-space: nowrap;
    }
  </style>
</head>
<body>
""")

print(f"""
<div class="status {html.escape(current_state)}">
  CURRENT STATUS: {html.escape(current_state)}<br>
  <span style="font-size: 0.6em; font-weight: normal;">
    since {format_ts(current["timestamp"])}
  </span>
</div>
""")

print("""
<h1>State Transitions</h1>

<table>
  <tr>
    <th>Timestamp</th>
    <th>Previous State</th>
    <th>New State</th>
    <th>Duration (s)</th>
    <th>Reason</th>
  </tr>
""")

for entry in reversed(data):
    prev_state = html.escape(entry["previous_state"])
    new_state = html.escape(entry["new_state"])
    reason = html.escape(entry["reason"])

    print(f"""
  <tr>
    <td>{format_ts(entry["timestamp"])}</td>
    <td class="state {prev_state}">{prev_state}</td>
    <td class="state {new_state}">{new_state}</td>
    <td class="duration">{entry["duration_seconds"]:.2f}</td>
    <td>{reason}</td>
  </tr>
""")

print("""
</table>

</body>
</html>
""")

