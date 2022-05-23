import shutil
import sys

from typing import List
from pathlib import Path

from docutils.core import publish_parts
from markdown import markdown
from ssg.content import Content

from ssg import hooks


class Parser:
    base_ext = ".html"
    file_exts: List[str] = []

    def valid_file_ext(self, file_ext):
        return file_ext in self.file_exts

    def parse(self, path: Path, source: Path, dest: Path):
        raise NotImplementedError

    def read(self, path):
        with open(path, "r") as file:
            return file.read()

    def write(self, path, dest, content):
        file_path = dest / path.with_suffix(self.base_ext).name
        with open(file_path, "w") as file:
            file.write(content)

    def copy(self, path, source, dest):
        shutil.copy2(path, dest / path.relative_to(source))


class ResourceParser(Parser):
    file_exts = [".jpg", ".png", ".gif", ".css", ".html"]

    def parse(self, path, source, dest):
        self.copy(path, source, dest)


class MarkdownParser(Parser):
    file_exts = [".md", ".markdown"]

    def parse(self, path, source, dest):
        content = Content.load(self.read(path))
        html = markdown(content.body)
        filtered = hooks.filter("generate_menu", html, self.base_ext)
        self.write(path, dest, filtered)
        sys.stdout.write(
            "\x1b[1;32m{} converted to HTML. Metadata: {}\n".format(path.name, content)
        )


class ReStructuredTextParser(Parser):
    file_exts = [".rst"]

    def parse(self, path, source, dest):
        content = Content.load(self.read(path))
        html = publish_parts(content.body, writer_name="html5")
        filtered = hooks.filter("generate_menu", html["html_body"], self.base_ext)
        self.write(path, dest, filtered)
        sys.stdout.write(
            "\x1b[1;32m{} converted to HTML. Metadata: {}\n".format(path.name, content)
        )
