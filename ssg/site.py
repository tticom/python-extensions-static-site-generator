import sys
from pathlib import Path
from ssg import extensions, hooks

class Site:
    def __init__(self, source, dest, parsers=None):
        self.source = Path(source)
        self.dest = Path(dest)
        self.parsers = parsers or []

    def create_dir(self, path):
        directory = self.dest / path.relative_to(self.source)
        directory.mkdir(parents=True, exist_ok=True)

    def load_parser(self, ext):
        for parser in self.parsers:
            if parser.valid_file_ext(ext):
                return parser

    def run_parser(self, path):
        parser = self.load_parser(path.suffix)
        if parser is not None:
            parser.parse(path, self.source, self.dest)
        else:
            self.error(
                "No parser for the {} extension, file skipped!".format(path.suffix)
            )

    def build(self):
        extensions.load_bundled()
        hooks.event("collect_files", self.source, self.parsers)
        self.dest.mkdir(parents=True, exist_ok=True)
        for path in self.source.rglob("*"):
            if path.is_dir():
                self.create_dir(path)
            elif path.is_file():
                self.run_parser(path)

    @staticmethod
    def error(message):
        sys.stderr.write("\x1b[1;31m{}\n".format(message))
