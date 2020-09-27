import argparse
import json

from xfconf import Xfconf


def main():
    argparser = argparse.ArgumentParser()
    argparser.add_argument(
        "--xq-path", type=str,
        help="Optional path to xion-query"
    )
    argparser.add_argument(
        "-e", "--export", type=str, nargs=3,
        metavar=("CHANNEL", "ROOT", "OUTPUT"),
        help=("Export settings in channel under this root. "
              "Use '/' as root to export the whole channel.")
    )
    argparser.add_argument(
        "-i", "--import", dest="import_tree", type=str,
        metavar=("JSON",),
        help="Import a JSON settings file"
    )
    argparser.add_argument(
        "-y", "--yes", action="store_true",
        help="Do not ask for confirmation"
    )
    args = argparser.parse_args()

    xion = Xion(xq=args.xq_path)
    if args.export:
        channel, root, output = args.export
        tree = xion.build_tree(channel, root)
        if tree is None:
            print("Failed to build config tree.")
            return
        xion.export_tree(channel, root, tree, output)
    elif args.import_tree:
        channel, root, tree = xion.import_tree(args.import_tree)
        if channel and root and tree:
            force = bool(args.yes)
            xion.apply_tree(channel, root, tree, confirm=not force)


class Xion:

    # GTypes to xfconf-query types along with a value string parser.
    TYPE_MAP = {
        "gboolean": "bool",
        "gint": "int",
        "guint": "uint",
        "gdouble": "double",
        "gchararray": "string",
    }

    def __init__(self, xq=None):
        self.xfconf = Xfconf(xq=xq)

    def build_tree(self, channel, root="/"):
        """Return a dict of configs in this channel, filtering on root.

        Return None on error.
        """
        if not root.startswith("/"):
            print("Invalid root, must start with /")
            return None
        props = self.xfconf.get_property_list(channel, root=root)
        if props is None:
            print(f"Failed to get property list for channel {channel}.")
            return None
        tree = {}
        for prop_name in props:
            prop = self.xfconf.get_property(channel, prop_name)
            if prop is None:
                print(f"Failed to get property {prop_name}.")
                return None
            if isinstance(prop, list):
                leaf = [Xion._build_prop_leaf(p) for p in prop]
            else:
                leaf = Xion._build_prop_leaf(prop)
            tree[prop_name] = leaf
        return tree

    def export_tree(self, channel, root, tree, output_path):
        """Export a config tree as a sorted JSON file."""
        tree["channel"] = channel
        tree["root"] = root
        with open(output_path, "wt") as output_file:
            json.dump(tree, output_file, indent=2, sort_keys=True)

    def import_tree(self, file_path):
        """Load a config tree."""
        with open(file_path, "rt") as input_file:
            tree = json.load(input_file)
        try:
            channel = tree.pop("channel")
            root = tree.pop("root")
        except KeyError:
            print("Missing channel or root in JSON.")
            return None, None, tree
        return channel, root, tree

    def apply_tree(self, channel, root, tree, confirm=True, replace=False):
        """Apply tree settings under root to channel."""
        num_changes = len(tree)
        print(f"Applying {num_changes} changes to {channel} under {root}.")
        if replace:
            print("This will erase all settings in the channel.")
        if confirm and input("Confirm? [y/N]") != "y":
            print("Operation cancelled.")
            return
        for prop, content in tree.items():
            self.apply_property(channel, prop, content)

    def apply_property(self, channel, name, content):
        """Update one property in Xfconf, return True on success."""
        # if isinstance(content, list):
        #     for subprop in content:
        #         if not self.apply_property(channel, 
        prop_type = content["type"]
        if not prop_type in Xion.TYPE_MAP:
            print(f"Unknown property type {prop_type}!")
            return False
        xq_type = Xion.TYPE_MAP[prop_type]
        value = content["value"]
        self.xfconf.set_property(channel, name, xq_type, value)

    @staticmethod
    def _build_prop_leaf(prop):
        return {"type": prop.gtype, "value": str(prop.value)}


if __name__ == "__main__":
    main()
