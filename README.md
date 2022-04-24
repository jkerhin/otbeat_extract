# Setup

This script requires Python 3.6 or higher and the `BeautifulSoup` library. Python best 
practices recommend using a virtual environment rather than installing directly alongside
your system Python.

In bash:  
```bash
python3 -m venv venv
source venv/bin/activate
python3 -m pip install -r requirements.txt
```

In PowerShell
```powershell
python3 -m venv venv
.\venv\Scripts\Activate.ps1
python3 -m pip install -r requirements.txt
```

# Use

You'll need to export all of the "OTbeatReport" emails to `.eml` files. With a desktop 
email client like Outlook or Thunderbird, this should be as simple as doing a search 
of "From: OTbeatReport@orangetheoryfitness.com", selecting all your messages, and then
dragging and dropping into a folder.

This is likely to be much more of a pain using webmail. I know that in GMail you can export
messages one at a time (Three dots-> Download message), but I don't have great advice on
bulk export.

Once you've got your emails downloaded, however, the script is quite easy to use:

```bash
source venv/bin/activate
python otbeat_extract.py /path/to/file1.eml /path/to/file2.eml
```

You can also pass in a glob (e.g. `otbeat_extract.py /path/to/file*.eml`), and you can
specify the name of your output CSV file (default: `otbeat.csv`):

```bash
python otbeat_extract.py -o my_csv.csv /path/to/file*.eml
```

To operate on an `mbox` single-file mailbox, use the `extract_mbox.py` script. This script
has the same `-o/--out-file` flag as `otbeat_extract.py`, but instead of operating on a 
list of `.eml` files, operates on an `mbox` mailbox.

```bash
python extract_mbox.py -o out_file.csv /path/to/mbox_file
```

# Background

This script differs from other parsers in that it runs entirely offline. The distinct 
advantage to running offline is that this script does not need any access to your email
account.

The distinct *disadvantage* is that you have to save out each OTbeatReport email as 
a ".eml" file, which is labor intensive and clunky from a webmail UI. Additionally,
this tool is command line only, with no user GUI, so it's not particularly friendly
to non-developers.

This approach was orignially inspired by /u/toluun on the OrangeTheory subreddit:
    https://www.reddit.com/r/orangetheory/comments/8usrp1/otf_email_scraperv2_no_computer_skills_required/

After writing my parser, I found that Jimmy Van Hout https://github.com/JimmyVanHout has
written a Python extractor as well: https://github.com/JimmyVanHout/otf_data

That parser also uses BeautifulSoup to extract fields, but the approach is _very_ different,
and the package uses IMAP to connect to a mail server and pull messges, instead of requiring 
the user to pull messages manually.

# Developing

If you're doing further development on this tool, use the `environment-dev.txt` when setting up
your virtualenv rather than the default `requirements.txt`. The big change that the development 
environment brings is `pre-commit`. Set up your development environment like so:

```bash
python3 -m venv venv
python3 -m pip install -r requirements-dev.txt
pre-commit install
# This should *not* find any errors, but may take a minute or so to get
# pre-commit set up for the first time
pre-commit run
```
