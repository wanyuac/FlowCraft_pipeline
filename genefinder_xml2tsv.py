#!/usr/bin/env python
"""
Compile GeneFinder's output XML files into a tab-delimited file.

Example command:
    python genefinder_xml2tsv.py -i output/*.xml 1> genes_detected.tsv 2> genes_detected.err

Note:
    1. Input filenames are not used for the output.
    2. PHE's GeneFinder: github.com/phe-bioinformatics/gene_finder
    3. Reference: https://www.geeksforgeeks.org/convert-xml-to-csv-in-python/

Copyright (C) 2021 Yu Wan <wanyuac@126.com>
Licensed under the GNU General Public Licence version 3 (GPLv3) <https://www.gnu.org/licenses/>.
First version: 6 Aug 2021; the latest update: 8 Aug 2021
"""

import os
import sys
import xml.etree.ElementTree as XML
from argparse import ArgumentParser


def parse_argument():
    parser = ArgumentParser(description = "Compile PHE GeneFinder output XML files into a TSV file")
    parser.add_argument('-i', '--input', dest = 'input', nargs = '+', type = str, required = True, help = "Input XML files")
    return parser.parse_args()


def main():
    args = parse_argument()
    print('\t'.join(['Isolate', 'Gene', 'Allele', 'Description', 'Certainty', 'Identity', 'Coverage', 'Coverage_distr', 'Depth', 'Mode',\
          'Report_type', 'DB_index', 'Alteration', 'Insertion', 'Deletion', 'Mix', 'Large_indel', 'Mismatch']), file = sys.stdout)
    for x in args.input:
        if os.path.exists(x):
            print(f"Parsing {x}.", file = sys.stderr)
            xml_root = XML.parse(x).getroot()  # type(xml_root): class 'xml.etree.ElementTree.Element'. Use dir(xml_root) to see its methods.
            sample = xml_root.attrib['id']  # The attrib method returns a dictionary
            sample = sample[ : len(sample) - 2]  # For an unknown reason, the sample name mistakenly has an '_1' suffix.
            results = xml_root[1][2 : ]  # Skip the first two entries: 'coverage_control' and 'mix_indicator'.
            for result in results:  # Each result (<result>) is an object of class 'xml.etree.ElementTree.Element'.
                allele = result.attrib['value']
                gene = allele.split('_')[0]  # GeneFinder interprets the underscore as the an indicator of an allele name.
                result_values = {'mode' : 'NA', 'alterations' : 'NA', 'detection' : 'NA', 'description' : 'NA', 'report_type' : 'NA',\
                                 'coverage' : 'NA', 'homology' : 'NA', 'depth' : 'NA', 'coverage_distribution' : 'NA', 'insertions' : 'NA',\
                                 'deletions' : 'NA', 'mix' : 'NA', 'large_indels' : 'NA', 'mismatch' : 'NA', 'modifications' : 'NA'}
                for result_data in result:
                    val_dict = result_data.attrib
                    val_type = val_dict['type']
                    val = val_dict['value']
                    if val_type == 'detection' and val == 'ND':  # Not detected: skip this record
                        proceed = False
                        break
                    else:
                        proceed = True
                        result_values[val_type] = val
                if proceed:
                    try:
                        report_type, index = result_values['report_type'].split('_')
                    except ValueError:
                        print(f"Error: report_type {result_values['report_type']} of allele {allele} in {x} cannot be parsed.", file = sys.stderr)
                        sys.exit(1)
                    if result_values['mode'] == 'regulator':
                        result_values['alterations'] = result_values['modifications']  # It weird that for regulatory genes, there is no 'alterations' attribute but 'modifications'.
                    print('\t'.join([sample, gene, allele, result_values['description'], result_values['detection'], result_values['homology'],\
                                     result_values['coverage'], result_values['coverage_distribution'], result_values['depth'], result_values['mode'],\
                                     report_type, index, result_values['alterations'], result_values['insertions'], result_values['deletions'],\
                                     result_values['mix'], result_values['large_indels'], result_values['mismatch']]), file = sys.stdout)
        else:
            print(f"Warning: XML file {x} is ignored as it is not accessible.", file = sys.stderr)
            continue
    return


if __name__ == '__main__':
    main()