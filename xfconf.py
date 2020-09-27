import re
import shutil
import subprocess
from dataclasses import dataclass


class Xfconf:
    """Interface around Xfconf, using xion-query behind the scene."""

    def __init__(self, xq=None):
        self._xq = xq or self.find_xq()

    def xq(self, command, print_failures=True):
        """Run a xion-query command and return its output or None on error."""
        command.insert(0, self._xq)
        try:
            return subprocess.check_output(
                command, stderr=subprocess.STDOUT
            ).decode()
        except subprocess.CalledProcessError as exc:
            if not print_failures:
                return None
            print(f"xion-query command failed with code {exc.returncode}.")
            if exc.stdout:
                print("stdout:", exc.stdout.decode().strip())
            if exc.stderr:
                print("stderr:", exc.stderr.decode().strip())
            return None

    def xqs(self, command_str, print_failures=True):
        """Wrapper of xq, splitting a string command."""
        return self.xq(command_str.split(" "), print_failures=print_failures)

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

    def does_property_exist(self, channel, prop):
        """Return True if this property exists."""
        output = self.xqs(f"-c {channel} -p {prop}", print_failures=False)
        return output is not None

    def get_property(self, channel, prop):
        """Return this property or None on error."""
        output = self.xqs(f"-c {channel} -p {prop}")
        if output is None:
            return None
        return XfconfProperty.parse(output)

    def set_property(self, channel, prop, prop_type, value):
        """Create or update this property."""
        if not self.does_property_exist(channel, prop):
            self.create_property(channel, prop, prop_type, value)
        else:
            self.update_property(channel, prop, value)

    def create_property(self, channel, prop, prop_type, value):
        """Create a new property with those params, return True on success."""
        if " " in value:
            value = f'"{value}"'
        output = self.xq(["-c", channel, "-p", prop, "-n",
                          "-t", prop_type, "-s", value])
        if output is None:
            return False

    def update_property(self, channel, prop, value):
        """Update an existing property, return True on success."""
        if " " in value:
            value = f'"{value}"'
        output = self.xq(["-c", channel, "-p", prop, "-s", value])
        return output == ""

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
