#!/usr/bin/env python
#encoding: utf-8
#
# This is a script for converting an xml file (from Appraise) into a csv file,
# extracting "pairwise comparisons" for each judgement with allowing multiple 
# systems for one translation.
# If the xml file includes reference as a system, you can exclude it by setting
# EXCLUDE_REF = True (True in default).

# Usage: python fromAppraise.xml
# Output: fromAppraise.csv

EXCLUDE_REF = True
N = 2 # extracting pairwise judgements

import sys
import os
import csv 
import itertools
import xml.etree.ElementTree as ET
from collections import Counter

def extract_all_judgements(rankings):
    systems_j = []
    ranks_j = []
    if len(ranking.findall(".//translation")) == 0:
        pass
    else:
        for i, rank in enumerate(ranking.findall(".//translation")):
            rank_i = rank.attrib['rank']
            for system_name in rank.attrib['system'].split(','):
                if EXCLUDE_REF and system_name[0:3] == 'ref':
                    pass
                else:
                    systems_j.append(system_name)
                    ranks_j.append(rank_i)

    return zip(systems_j, ranks_j)


xmlPath = sys.argv[1]
csvPath = xmlPath.split('.xml')[0] + '.csv'
csvFile = open(csvPath, 'w')
elem = ET.parse(xmlPath).getroot()

header_fields = 'srclang,trglang,srcIndex,judgeID,system1Id,system1rank,system2Id,system2rank'.split(',')
writer = csv.DictWriter(csvFile, fieldnames=header_fields)

writer.writeheader()

hits = elem.findall(".//HIT")
for hit in hits:
    source_lang = hit.attrib['source-language']
    target_lang = hit.attrib['target-language']

    rankings = hit.findall(".//ranking-task")

    for ranking in rankings:
        for result in ranking.findall(".//ranking-result"):
            csv_row = {}
            csv_row['srcIndex'] = ranking.attrib['id']
            csv_row['srclang'] = source_lang
            csv_row['trglang'] = target_lang
            csv_row['judgeID'] = result.attrib['user']

            systems_ranks = extract_all_judgements(result)
            for element in itertools.combinations(systems_ranks, N):
                for i, system_rank in enumerate(element):
                    systemID = "system{}Id".format(str(i+1))
                    systemRank = "system{}rank".format(str(i+1))
                    csv_row[systemID] = system_rank[0]
                    csv_row[systemRank] = system_rank[1]

                writer.writerow(csv_row)

csvFile.close()
