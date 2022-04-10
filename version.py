#!/usr/bin/python3

import subprocess


class VersionComponent:
    def __init__(self, next_component=None) -> None:
        self.number = 0
        self._next = next_component

    def set(self, number: int) -> None:
        self.number = number
        if self._next:
            self._next.set(0)

    def increment(self) -> None:
        self.set(self.number + 1)

    def __str__(self):
        return str(self.number)


class SemVersion:
    def __init__(self):
        self.patch = VersionComponent()
        self.minor = VersionComponent(self.patch)
        self.major = VersionComponent(self.minor)
        self.appendix: str = None

    def __str__(self):
        ret = ".".join([str(self.major), str(self.minor), str(self.patch)])
        if self.appendix:
            ret += f"-{self.appendix}"
        return ret


def read_from_git(repo_path: str = "."):
    ret = SemVersion()

    log_lines = []
    r = subprocess.run(["git", "log"], cwd=repo_path, stdout=subprocess.PIPE)
    log_lines = r.stdout.decode().splitlines()
    commit_lines = []
    commit_segment = None
    for line in log_lines:
        tokens = line.split(" ")
        if len(tokens) == 2 and tokens[0] == "commit":
            if commit_segment:
                commit_lines.append(commit_segment)
            commit_segment = []
        commit_segment.append(line)

    for segment in reversed(commit_lines):
        _analyze_commit(segment, ret)

    return ret


def _analyze_commit(commit_log, version):
    is_merge = False
    version_commands = []
    for line in commit_log:
        if line.startswith("Merge: "):
            is_merge = True
        if line.startswith("    version."):
            version_commands.append(line.strip())
    if len(version_commands) > 0:
        for command in version_commands:
            if command == "version.patch++":
                version.patch.increment()
            if command == "version.minor++":
                version.minor.increment()
            if command == "version.major++":
                version.major.increment()
    elif is_merge:
        version.minor.increment()


def main():
    v = read_from_git()
    print(v)


if __name__ == "__main__":
    main()
