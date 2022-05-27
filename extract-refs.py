#!/usr/bin/env python3

from collections import defaultdict
import json
import re
from os import path
import sys
import xml.sax

MAX_RFC = 10000
RFC_DIR = "rfcs"

EXCEPTIONS = []


def main(existing_data=None):
    refs = existing_data or {}
    for num in range(1, MAX_RFC):
        num = str(num)
        if num in refs:
            continue
        if num in EXCEPTIONS:
            continue
        results = None
        if path.exists(f"{RFC_DIR}/rfc{num}.xml"):
            results = parse_xml(num)
        elif path.exists(f"{RFC_DIR}/rfc{num}.txt"):
            results = parse_txt(num)
        else:
            continue
        for result_type in ["normative", "informative"]:
            if results and not len(results[result_type]):
                del results[result_type]
        refs[num] = results

    return refs


### Text Parsing
###
### This is awful, but blessedly temporary; all new RFCs are published in XML.

blank_line = re.compile("^\s*$")
ref_section_line = re.compile(
    "^\s*((\d+|[A-N])(\.\d+){0,1}\.?\s+)?((Normative|Non-[Nn]ormative|Informative|Informational) )?[Rr]eferences?\s*$"
)
normative = re.compile("normative", re.IGNORECASE)
informative = re.compile("(informative|informational|non-normative)", re.IGNORECASE)
ref_line = re.compile("RFC[ -]?(\d+)")
header_line = re.compile(
    "^\s?RFC\s?\d{1,5}\s+[\s\w\d\-\./()&,+:'\"*#!?;=]+\s+([A-Z][a-z]+)\s\d{4}$"
)
footer_line = re.compile("^\w[\s\w\d\-\./()&,+:'\"*#!?;=]+\s{3,}\[[Pp]age \d+\]$")
section_header = re.compile("^[\w\d].*$", re.IGNORECASE)
common_post_sections = re.compile(
    "^((\d+|[A-N])(\.\d+){0,3}\.?\s+)?((Contributing )?(Contact|Author|Editor|Contributor|Chair)'?s?'?\s+(Address(es)?|Information)?:?|Contributors|Co-Authors|Chair, Editor, and Author'?s?'? Addresses|Contacts|Authors and Acknowledgements|Acknowl?edge?ments?|Security Considerations|IANA Considerations|Full Copyright Statement|Intellectual Property( Statement| Notice)?|IAB Members at the Time of (Approval|This Writing)|Reference Conventions|Index|Bibliography|Notes|Notices|Disclaimer|URIs|Change Log|Acronyms)\s*$|Changes (From|Since) RFC|Appendix|Annex A",
    re.IGNORECASE,
)


def parse_txt(rfc_num):
    with open(f"{RFC_DIR}/rfc{rfc_num}.txt", "r", encoding="latin-1") as fh:
        refs = {"normative": [], "informative": []}
        line_num = 0
        blank_before = False
        in_r = False
        in_n = False
        in_i = False
        for line in fh.readlines():
            line_num += 1
            if blank_line.match(line):
                blank_before = True
                continue
            if blank_before and ref_section_line.match(line):
                #                print(f"rfc{rfc_num}:{line_num}\t\t{line.strip()}")
                if normative.search(line):
                    in_r = in_i = False
                    in_n = True
                elif informative.search(line):
                    in_r = in_n = False
                    in_i = True
                else:
                    in_n = in_i = False
                    in_r = True
            elif in_r or in_i or in_n:
                if section_header.match(line):
                    if header_line.match(line) or footer_line.match(line):
                        pass  # page header / footer
                    else:
                        in_r = in_i = in_n = False  # section header
                #     if not common_post_sections.search(line):
                #         sys.stderr.write(
                #             f"Unusual section header: {rfc_num}:{line_num}\t{line.strip()}\n"
                #         )
                else:
                    ref_rfc = ref_line.search(line)
                    if ref_rfc:
                        ref_type = in_i and "informative" or "normative"
                        ref = ref_rfc.group(1)
                        if int(ref) == int(rfc_num):
                            in_r = False  # Bad habit of yang modules. False positives in the mid-1440's
                        elif ref not in refs[ref_type]:
                            refs[ref_type].append(ref)
            blank_before = False
    return refs


### XML Parsing

def parse_xml(rfc_num):
    with open(f"{RFC_DIR}/rfc{rfc_num}.xml", "r", encoding="utf-8") as fh:
        parser = xml.sax.make_parser()
        handler = RfcHandler()
        parser.setContentHandler(handler)
        parser.parse(fh)
    return handler.refs


class RfcHandler(xml.sax.handler.ContentHandler):
    sections = {
        "normative references": "normative",
        "informative references": "informative",
    }

    def __init__(self):
        self.refs = {"normative": [], "informative": []}
        self.ref_section = "normative"
        self.content = ""
        self.tags = []
        self.feature_namespaces = True
        xml.sax.handler.ContentHandler.__init__(self)

    def startElement(self, name, attrs):
        if name == "seriesInfo" and self.tags[-1] == "reference":
            if attrs.get("name").upper() == "RFC":
                if attrs.get("value") not in self.refs[self.ref_section]:
                    self.refs[self.ref_section].append(attrs.get("value"))
        self.tags.append(name)

    def characters(self, content):
        self.content += content

    def endElement(self, name):
        tag = self.tags.pop()
        assert tag == name
        if tag == "name" and self.tags[-1] == "references":
            self.ref_section = self.sections.get(
                self.content.strip().lower(), "normative"
            )
        self.content = ""


if __name__ == "__main__":
    if len(sys.argv) > 1:
        with open(sys.argv[1], "r") as fh:
            existing_data = json.load(fh)
        refs = main(existing_data)
    else:
        refs = main()
    print(json.dumps(refs, indent=2, sort_keys=True, default=lambda a: list(a)))
