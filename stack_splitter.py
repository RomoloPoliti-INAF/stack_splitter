#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import xml.etree.ElementTree as ET

ET._namespace_map['http://edds.egos.esa/model'] = 'ns2'
top = ET.Element("{http://edds.egos.esa/model}ResponsePart")

class Stack:
    def __init__(self):
        self.outRoot = ET.ElementTree(top)
        self.child1 = ET.SubElement(top, 'Response')
        self.child2 = ET.SubElement(self.child1, 'PktTcReportResponse')
        
    def add(self, packet):
        self.child2.append(packet)
        
    def write(self, output):
        self.outRoot.write(output, encoding='utf-8', xml_declaration=True)

def search(packet, label):
    for child in packet:
        if child.tag == label:
            return child.text
def stack_splitter(fileName):
    myDoc = ET.parse(fileName)
    root = myDoc.getroot()
    
    
    stacks={}
    for packet in root.iter('PktTcReportListElement'):
        dt = search(packet, 'ReleaseTime').split('.')[0]
        if dt in stacks.keys():
            stacks[dt].add(packet)
        else:
            stacks[dt] = Stack()
            stacks[dt].add(packet)
    
    for key in stacks.keys():
        stacks[key].write(f"output/{key}.xml")





if __name__ == "__main__":
    fileName = "input/00_-_ICO11_-_All_Tests_-_TC.xml"
    stack_splitter(fileName)
    print("Done")