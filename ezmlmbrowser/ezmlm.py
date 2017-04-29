#!/usr/bin/env

"""ezmlm archive reader functions.

"""

import os

import email
parser = email.parser.Parser()

class List:
    """An object representing an ezmlm mailing list.

    Or, more like, its archive – the List object knows its server and
    name, but mostly it knows where to find the list archive.

    """

    def __init__(self, name, path="/etc/ezmlm"):
        self.name = name
        self.path = os.path.join(path, self.name)
        self.description = ""
        try:
            with open(os.path.join(
                    self.path, "text", "info")) as info:
                for l, line in enumerate(info):
                    if l == 0:
                        self.shortdescr = line
                    else:
                        self.description += line
        except FileNotFoundError:
            self.shortdescr = self.name
        months = os.listdir(os.path.join(
            self.path, "archive", "threads"))
        self.months = sorted([
            (int(m[:-2]), int(m[-2:]))
            for m in months], reverse=True)

        self.min_msg = float("inf")
        self.max_msg = 0
        for m in os.listdir(os.path.join(
                self.path, "archive")):
            try:
                m_block = 100 * int(m)
                if m_block < self.min_msg or (
                        m_block + 100 > self.max_msg):
                    for n in os.listdir(os.path.join(
                            self.path, "archive", m)):
                       n = m_block + int(n)
                       if n < self.min_msg:
                           self.min_msg = n
                       if n > self.max_msg:
                           self.max_msg = n
            except ValueError:
                pass
                    
        self._files = {}
        self._actual_subjects = {}
        self._threads = {}

    def file_loader(self, path):
        """Read the file and cache it."""
        if path not in self._files:
            with open(os.path.join(self.path, path)) as file:
                self._files[path] = file.read()
        return self._files[path]

    def by_number(self, number):
        content = self.file_loader(os.path.join(
            "archive", "{:d}".format(number // 100),
            "{:02d}".format(number % 100)))
        mail = parser.parsestr(content)
        self._actual_subjects[number] = mail["Subject"]
        return mail

    def subject(self, number):
        try:
            return self._actual_subjects[number]
        except KeyError:
            return self.by_number(number)["Subject"]

    def by_author(self, a_hash):
        content = self.file_loader(os.path.join(
            "archive", "authors", a_hash[:2], a_hash[2:]))
        raw_author, raw_messages = content.split("\n", 1)
        h, name = raw_author.split(" ", 1)
        assert a_hash == h
        for message in raw_messages.split("\n"):
            if not message.strip():
                continue
            n, month, rest = message.split(":", 2)
            n = int(n)
            subject_id, subject = rest.split(" ", 1)
            yield {"n": n,
                   "month": int(month[-2:]),
                   "year": int(month[:-2]),
                   "author_id": a_hash,
                   "subject": subject,
                   "subject_id": subject_id,
                   "author": name}

    def thread_for_message(self, number):
        try:
            return self._threads[number]
        except KeyError:
            index = self.file_loader(os.path.join(
                "archive", "{:d}".format(number // 100),
                "index"))
            line = index.split("\n")[(number % 100 - 1) * 2]
            assert line.startswith(str(number % 100))
            _, thread, subject = line.split(" ", 2)
            self._actual_subjects[number] = subject
            self._threads[number] = thread
            return self._threads[number]

    def by_thread(self, s_hash):
        content = self.file_loader(os.path.join(
            "archive", "subjects", s_hash[:2], s_hash[2:]))
        raw_subject, raw_messages = content.split("\n", 1)
        h, subject = raw_subject.split(" ", 1)
        assert s_hash == h
        for message in raw_messages.split("\n"):
            if not message.strip():
                continue
            n, month, rest = message.split(":", 2)
            n = int(n)
            author_id, author = rest.split(" ", 1)
            yield {"n": n,
                   "month": int(month[-2:]),
                   "year": int(month[:-2]),
                   "author_id": author_id,
                   "subject": self.subject(n),
                   "subject_id": s_hash,
                   "author": author}

    def by_date(self, year, month=None):
        threads = self.file_loader(os.path.join(
            "archive", "threads", "{:d}{:02d}".format(year, month)))
        for thread in threads.split("\n"):
            if not thread.strip():
                continue
            n, rest = thread.split(":", 1)
            thread_hash, how_many, subject = rest.split(" ", 2)
            how_many = int(how_many[1:-1])
            yield {"subject": subject,
                   "thread": thread_hash,
                   "n": int(n),
                   "messages": how_many}

