#!/usr/bin/env python3
"""Extension of otbeat_extract.py to extract from single-file `mbox` Mailbox files

TODO: Need to rearchitect both this and otbeat_extract.py to share code more reasonably
"""
import argparse
from email import policy
from email.parser import BytesParser
from io import BytesIO
from mailbox import mbox, mboxMessage

from bs4 import BeautifulSoup

from otbeat_extract import extract_data, get_datetime, write_csv


def get_mbox_soup(msg: mboxMessage) -> BeautifulSoup:
    """Extract the HTML contents of an mbox message and parse with BeautifulSoup"""
    fakefile = BytesIO(msg.as_bytes())
    parsed = BytesParser(policy=policy.default).parse(fakefile)
    raw_html = parsed.get_body().get_content()
    return BeautifulSoup(raw_html, "html.parser")


def main():
    parser = argparse.ArgumentParser(
        description="Read a mailbox file in the 'mbox' format and extract OTBeatReport data"
    )
    parser.add_argument(
        "-o",
        "--out-file",
        default="otbeat.csv",
        help="Output CSV filename. Default: %(default)s",
    )
    parser.add_argument("mbox", help="mbox mailbox to extract data from")
    args = parser.parse_args()

    box = mbox(args.mbox)

    parsed_metrics = [
        extract_data(get_mbox_soup(msg))
        for msg in box.values()
        if msg["From"] == "OTbeatReport@orangetheoryfitness.com"
    ]
    sorted_metrics = sorted(parsed_metrics, key=get_datetime)
    write_csv(sorted_metrics, args.out_file)


if __name__ == "__main__":
    main()
