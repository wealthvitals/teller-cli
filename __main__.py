import cmd
import os
import re
import argparse
import pdfplumber
from institution.rbc import InstitutionRBC
from enum import Enum

class LoadFileType(Enum):
    PDF = "PDF"
    CSV = "CSV"

class InstitutionType(Enum):
    RBC = "RBC"

class CLI(cmd.Cmd):
    prompt = 'λ '
    intro = 'Welcome to Teller, a CLI for all sorts of personal finance goodies. Type "help" for available commands.'

    def __init__(self):
        super().__init__()

    def _parse_args(self, args=None):
        parser = argparse.ArgumentParser()
        parser.add_argument("institution", type=str, help="The institution who issued the bank statement")
        parser.add_argument("filepath", type=str, help="The file path of the bank statement")
        parser.add_argument("-t", "--filetype", type=str, default="CSV", choices=[e.value for e in LoadFileType],
                            help="The file type of the bank statement")
        parser.add_argument("-d", "--debug", action="store_true", default=False,
                            help="Enable debug mode (more verbose output)")
        return parser.parse_args(args)
    
    def do_load(self, arg):
        """Loads the contents of a bank statement file."""
        args = self._parse_args(arg.split())
        try:
            self._load(args.institution, args.filetype, args.filepath, args.debug)
        except Exception as e:
            print(f"Error: {e}")

    def do_quit(self, arg):
        """Exit the CLI"""
        return True
    
    def do_exit(self, arg):
        return self.do_quit(arg)

    def _load(self, institution, filetype, filepath, debug):
        # Hardcoded for now
        rbc = InstitutionRBC()
        text = ""
        with pdfplumber.open(filepath) as pdf:
            for page in pdf.pages:
                text += page.extract_text(x_tolerance=1)
            if (debug):
                print(text)
                return
        rbc.load_stmt_pdf(text)


if __name__ == '__main__':
    CLI().cmdloop()

