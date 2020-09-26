import re
import shutil
import subprocess
from dataclasses import dataclass


class Xfconf:
    """Interface around Xfconf, using xion-query behind the scene."""

    def __init__(self, xq=None):
        self._xq = xq or self.find_xq()

    def xq(self, command):
        """Run a xion-query command and return its output or None on error."""
        command.insert(0, self._xq)
        try:
            return subprocess.check_output(command).decode()
        except subprocess.CalledProcessError as exc:
            print(exc)
            return None

    def xqs(self, command_str):
        """Wrapper of xq, splitting a string command."""
        return self.xq(command_str.split(" "))

    def get_channel_list(self):
        """Return the channel list or None on error."""
        output = self.xqs("-l")
        if output is None:
            return None
        return output.splitlines()

    def get_property_list(self, channel, root="/"):
        """Return the property list for this channel or None on error."""
        output = self.xqs(f"-c {channel} -l")
        if output is None:
            return None
        return [p for p in output.splitlines() if p.startswith(root)]

    def get_property(self, channel, prop):
        """Return this property or None on error."""
        output = self.xqs(f"-c {channel} -p {prop}")
        if output is None:
            return None
        return XfconfProperty.parse(output)

    @staticmethod
    def find_xq():
        xq = shutil.which("xion-query")
        if not xq:
            exit("Could not find xion-query in path.")
        return xq


XION_PROP_RE = re.compile(r"t:(\S+) (.+)")


@dataclass
class XfconfProperty:
    """Hold type and value for an Xfconf property."""
    gtype: str
    value: None = None

    @staticmethod
    def parse(prop_str):
        if prop_str.startswith("a:"):
            return XfconfProperty.parse_array(prop_str)
        return XfconfProperty._parse_property(prop_str)

    @staticmethod
    def parse_array(prop_str):
        expected_length = 0
        properties = []
        for line in prop_str.splitlines():
            if line.startswith("a:"):
                try:
                    expected_length = int(line.split(":")[1])
                except ValueError:
                    print("Failed to get expected array length.")
                    return None
            elif line.startswith("t:"):
                prop = XfconfProperty._parse_property(line)
                if not prop:
                    return None
                properties.append(prop)
        if len(properties) != expected_length:
            print(f"Number of properties ({len(properties)}) received "
                  f"is different than expected ({expected_length}).")
        return properties

    @staticmethod
    def _parse_property(prop_str):
        match = XION_PROP_RE.match(prop_str)
        if not match:
            print(f"Failed to parse '{prop_str}'.")
            return None
        return XfconfProperty(gtype=match.group(1), value=match.group(2))
