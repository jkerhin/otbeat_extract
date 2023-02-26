#!/usr/bin/env python3
"""Simple script to extract data from OrangeTheory "OTbeatReport" emails

This script runs entirely offline, but does require the user to have exported all
of their OTbeatReport emails to ".eml" files
"""
import argparse
from csv import DictWriter
from datetime import datetime
from email import policy
from email.parser import BytesParser
from pathlib import Path

from bs4 import BeautifulSoup, NavigableString, Tag


def get_email_soup(email_pth: Path) -> BeautifulSoup:
    """Extract HTML content from email message, parse with BeautifulSoup"""
    with email_pth.open("rb") as hdl:
        msg = BytesParser(policy=policy.default).parse(hdl)
    raw_html = msg.get_body().get_content()
    return BeautifulSoup(raw_html, "html.parser")


def extract_peak_hr(peak_hr_root: Tag) -> str:
    """Peak Heart Rate's 'span' needs special extraction logic"""
    peak_hr_children = list(peak_hr_root.children)
    tag = peak_hr_children[1]
    if isinstance(tag, NavigableString):
        # Current style
        return str(tag)
    elif isinstance(tag, Tag):
        # Old style, need to extract text
        return tag.text
    else:
        # Unknown style
        raise ValueError(f"Unable to extract peak heart rate from {tag}")


def extract_data(soup: BeautifulSoup) -> dict:
    """Identify the report format, and call the correct extract function

    TODO: I only have one report prior to 2022. If there are additional formats
        that cannot be parsed with the current code, please let me know

    """
    if soup.find(text="STUDIO WORKOUT SUMMARY"):
        return extract_current(soup)
    else:
        return extract_previous(soup)


def extract_current(soup: BeautifulSoup) -> dict:
    """Extract metrics from a current (April 2022) OTbeatReport email

    TODO: Document when this format began

    """
    para_with_class = [p for p in soup.find_all("p") if p.get("class")]
    tag_index = {
        "studio": 1,
        "date": 2,
        "time": 3,
        "instructor": 4,
        "gray_minutes": 5,
        "blue_minutes": 6,
        "green_minutes": 7,
        "orange_minutes": 8,
        "red_minutes": 9,
        "calories": 11,
        "splat_points": 13,
        "avg_heart_rate": 15,
        "peak_heart_rate": 17,  # Need to special-case extract
        "steps": 19,
    }
    extracted_data = {
        field: para_with_class[ix].text for field, ix in tag_index.items()
    }
    extracted_data["peak_heart_rate"] = extract_peak_hr(
        para_with_class[tag_index["peak_heart_rate"]]
    )
    extracted_data["time"] = extracted_data["time"].replace(
        "\u200c", ""
    )  # Remove zero width non-joiner
    # Extra spaces starting c. September 2022...
    for key in extracted_data:
        extracted_data[key] = extracted_data[key].strip()
    return extracted_data


def extract_previous(soup: BeautifulSoup) -> dict:
    """Extract metrics from an OTbeatReport email using older style formatting

    Note that this report also includes "Avg. % of Max Heart-Rate", but since the
    current reports do not include this metric, it's not being extracted in order
    to remain consistent with the new-style reports

    TODO: Document when this format began, ended. The only example I have is
        from October 2018

    """
    para_with_class = [p for p in soup.find_all("p") if p.get("class")]
    tag_index = {
        "studio": 1,
        "date": 0,
        "time": 2,
        "instructor": 4,
        "gray_minutes": 5,
        "blue_minutes": 6,
        "green_minutes": 7,
        "orange_minutes": 8,
        "red_minutes": 9,
        "calories": 10,
        "splat_points": 12,
        "avg_heart_rate": 14,
        "peak_heart_rate": 16,  # Need to special-case extract
        # Steps are not present in this report
    }
    extracted_data = {
        field: para_with_class[ix].text for field, ix in tag_index.items()
    }
    extracted_data["peak_heart_rate"] = extract_peak_hr(
        para_with_class[tag_index["peak_heart_rate"]]
    )
    extracted_data["time"] = (
        extracted_data["time"]
        .replace("\u200c", "")  # Remove zero width non-joiner
        .replace(": ", ":")  # And for some reason there was a space after :
    )
    # Reformat the date from MM.DD.YY to MM/DD/YYYY
    # OTF was founded in 2010, so don't have to worry about pre-1990 dates
    m, d, y = extracted_data["date"].split(".")
    extracted_data["date"] = "/".join((m, d, f"20{y}"))
    return extracted_data


def get_datetime(extracted_data: dict) -> datetime:
    datetime_str = f'{extracted_data["date"]} {extracted_data["time"]}'
    return datetime.strptime(datetime_str, "%m/%d/%Y %I:%M %p")


def write_csv(extracted_metrics: list, out_filename: str):
    with open(out_filename, "w", newline="") as hdl:
        writer = DictWriter(hdl, fieldnames=extracted_metrics[-1].keys())
        writer.writeheader()
        writer.writerows(extracted_metrics)


def main():
    parser = argparse.ArgumentParser(
        description="Read a set of OTbeatReport .eml files, extract data, and write to CSV"
    )
    parser.add_argument(
        "-o",
        "--out-file",
        default="otbeat.csv",
        help="Output CSV filename. Default: %(default)s",
    )
    parser.add_argument("eml_files", nargs="+", help="Email files to extract data from")
    args = parser.parse_args()

    # Expand globs
    # Implementing in Python because I don't feel like fighting with PowerShell
    eml_pths = []
    for arg in args.eml_files:
        pth = Path(arg)
        if "*" in arg:
            # Is this... good? It won't work if there's a glob in the directory path...
            eml_pths.extend(pth.parent.glob(pth.name))
        else:
            eml_pths.append(pth)

    parsed_metrics = [extract_data(get_email_soup(pth)) for pth in eml_pths]
    sorted_metrics = sorted(parsed_metrics, key=get_datetime)
    write_csv(sorted_metrics, args.out_file)


if __name__ == "__main__":
    main()
