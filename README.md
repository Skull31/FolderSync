<h1 align="center">FolderSync</h1>

<h3>Description</h3>

<p>Script written in Python which is scanning two folders and will synchronize everything from source folder to replica folder.</p>

<h3>Usage</h3>

<p>Script takes 4 input arguments:
  <ul>
    <li>-s - Source Folder Path - Required - Folder need to exist, otherwise the script will be terminated.</li>
    <li>-r - Replica Folder Path - Required - Folder need to exist, otherwise the script will be terminated.</li>
    <li>-i - Interval between synchronization - Not required, if not provided default interval will be 1 minute</li>
    <ul>
    <li>Interval needs to be in format integer + h/m/s (hour/minute/second)</li>
    </ul>
    <li>-l - Log file path - Not requied, but output won't be logged if not provided.</li>
  </ul>

Script can be terminated by Ctrl+C

Script was tested with Python version 3.9 and 3.10.

<h4>Example of usage</h4>

python FolderSync.py -s ~/SourceFolder -r ~/ReplicaFolder -i 1m -l ~/log.log

<h4>Script is compatible with following systems:</h4>

  <ul>
    <li>Windows - Tested on Windows 11</li>
    <li>Linux - Tested on Rocky Linux 9</li>
    <li>Potentially also MacOs but <b>Not Tested<b></li>
  </ul>
</p>
