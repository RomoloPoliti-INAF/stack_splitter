#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import xml.etree.ElementTree as ET
import rich_click as click
from rich.console import Console
from rich.progress import Progress, BarColumn, SpinnerColumn, TimeElapsedColumn
from pathlib import Path

__version__ = '0.1.0'
ET._namespace_map['http://edds.egos.esa/model'] = 'ns2'
top = ET.Element("{http://edds.egos.esa/model}ResponsePart")
console = Console()

# Progress bar settings
progresSet = [SpinnerColumn(finished_text=':thumbs_up-emoji:'),
              "[progress.description]{task.description}",
              BarColumn(finished_style='green'),
              "[progress.percentage]{task.percentage:>3.0f}%",
              "{task.completed:>6d} of {task.total:6d}",
              TimeElapsedColumn(),
              ]

# Program epilog string
progEpilog = "- For any information or suggestion please contact " \
    "[bold magenta]Romolo.Politi@inaf.it[/bold magenta]"

click.rich_click.USE_RICH_MARKUP = True
click.rich_click.FOOTER_TEXT = progEpilog
click.rich_click.HEADER_TEXT = f"Command Stack splitter, version [blue]{
    __version__}[/blue]"

# Context settings
CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])

# Messages


class MSG:
    ERROR = "[red][ERROR][/red] "
    CRITICAL = "[red][CRITICAL][/red] "
    INFO = "[green][INFO][/green] "
    DEBUG = "[blue][DEBUG][/blue] "
    WARNING = "[yellow][WARNING][/yellow] "


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


def stack_splitter(fileName: Path, output: Path = None, summary: bool = False, show_progress: bool = True, debug: bool = False, verbose: int = 0) -> None | dict[str, int]:
    if verbose > 0:
        console.print(f"{MSG.INFO}Processing file {
                      fileName}", style="bold blue")
    myDoc = ET.parse(fileName)
    root = myDoc.getroot()

    stacks = {}
    with Progress(*progresSet, console=console, transient=not show_progress) as progress:
        stack = progress.add_task("[green]Processing...", total=len(root))
        for packet in root.iter('PktTcReportListElement'):
            dt = search(packet, 'ReleaseTime').split('.')[0]
            if dt in stacks.keys():
                if summary:
                    stacks[dt] += 1
                else:
                    stacks[dt].add(packet)
            else:
                if debug:
                    console.print(f"{MSG.DEBUG}Creating stack for {
                                  dt}", style="bold blue")
                if summary:
                    stacks[dt] = 1
                else:
                    stacks[dt] = Stack()
                    stacks[dt].add(packet)
            progress.update(stack, advance=1)
    if summary:
        return stacks
    else:
        for key in stacks.keys():
            stacks[key].write(
                f"{output if not output is None else ''}/{fileName.stem}_{key}.xml")
        return None


@click.command(context_settings=CONTEXT_SETTINGS,)
@click.argument('fileName', type=click.Path(exists=True, path_type=Path, dir_okay=False, file_okay=True),
                metavar="FILENAME", required=True)
@click.option('-o', '--output', type=click.Path(dir_okay=True, file_okay=False, path_type=Path), metavar="OUTPUT",
              help="Optional output folder", default=None)
@click.option('-s', '--summary', is_flag=True, help="Print a summary of the process", default=False)
@click.option('--progress/--no-progress', 'show_progress', default=True, help="Enable or disable progress bar", show_default=True)
@click.option('-d', '--debug', is_flag=True,
              help="Enable :point_right: [yellow]debug mode[/yellow] :point_left:", default=False)
@click.option('-v', '--verbose', count=True, metavar="", help="Enable :point_right: [yellow]verbose mode[/yellow] :point_left:", default=0)
@click.version_option(__version__, '-V', '--version')
def action(filename: Path, output: Path, summary: bool, show_progress: bool, debug: bool, verbose: int) -> None:
    ret = stack_splitter(filename, output, summary,
                         show_progress, debug, verbose)
    if summary:
        print(ret)


if __name__ == "__main__":
    fileName = "input/00_-_ICO11_-_All_Tests_-_TC.xml"
    # stack_splitter(fileName)
    # print("Done")
    action()
