import argparse
import json

from xfconf import Xfconf


DEFAULT_FILE_PATH = "xion.json"


def main():
    argparser = argparse.ArgumentParser()
    argparser.add_argument("--xq-path", type=str,
                           help="Optional path to xion-query")
    argparser.add_argument("-e", "--export", type=str, nargs=2,
                           metavar=("channel", "root"),
                           help="Channel and root to export")
    argparser.add_argument("-f", "--file", type=str,
                           help="JSON file for import/export")
    args = argparser.parse_args()

    xion = Xion(xq=args.xq_path)
    if args.export:
        channel, root = args.export
        tree = xion.build_tree(channel, root)
        if tree is None:
            print("Failed to build config tree.")
            return
        if args.file:
            output_path = args.file
        else:
            print(f"No output file, using {DEFAULT_FILE_PATH}.")
            output_path = DEFAULT_FILE_PATH
        xion.export_tree(tree, output_path)


class Xion:

    def __init__(self, xq=None):
        self.xfconf = Xfconf(xq=xq)

    def build_tree(self, channel, root="/"):
        """Return a dict of configs in this channel, filtering on root.

        Return None on error.
        """
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

    def export_tree(self, tree, output_path):
        """Export a config tree as a sorted JSON file."""
        with open(output_path, "wt") as output_file:
            json.dump(tree, output_file, indent=2, sort_keys=True)

    @staticmethod
    def _build_prop_leaf(prop):
        return {"type": prop.gtype, "value": str(prop.value)}


if __name__ == "__main__":
    main()
