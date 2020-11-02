import json

from xion.xfconf import Xfconf


class Xion:
    """Manipulate Xfconf settings trees."""

    def __init__(self, xq=None, verbose=False):
        self.xfconf = Xfconf(xq=xq, verbose=verbose)
        self.verbose = verbose

    def build_tree(self, channel, root="/"):
        """Return a dict of properties in this channel, filtering on root.

        Return None on error. Root has to start with "/" to be valid. Arrays are
        added to the tree as a list of properties.
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

    @staticmethod
    def _build_prop_leaf(prop):
        return {"type": prop.gtype, "value": str(prop.value)}

    def export_tree(self, channel, root, tree, output_path):
        """Export a property tree as a sorted JSON file."""
        tree["channel"] = channel
        tree["root"] = root
        with open(output_path, "wt") as output_file:
            json.dump(tree, output_file, indent=2, sort_keys=True)

    def import_tree(self, file_path):
        """Load a property tree."""
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
        """Apply tree settings under root to channel, return True on success."""
        num_changes = len(tree)
        print(f"{num_changes} changes to do in {channel} for {root}.")
        if replace:
            print("This will erase all properties in the channel.")
        if confirm and input("Confirm? [y/N]") != "y":
            print("Operation cancelled.")
            return False
        if replace:
            if not self.clear_tree(channel, root):
                print("Failed to clear properties.")
                return False
        for prop, content in tree.items():
            if not self.apply_property(channel, prop, content):
                print(f"Failed to apply property {prop}.")
                return False
        print("Done.")
        return True

    def clear_tree(self, channel, root):
        """Remove all channel configs under root, return True on success."""
        return self.xfconf.reset_root(channel, root)

    def apply_property(self, channel, name, content):
        """Update one property in Xfconf, return True on success."""
        if isinstance(content, list):
            return self.xfconf.set_property_array(channel, name, content)
        prop_type = content["type"]
        value = content["value"]
        return self.xfconf.set_property(channel, name, prop_type, value)
