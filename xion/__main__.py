import argparse

from xion.xion import Xion


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
        "-r", "--replace", action="store_true",
        help="Replace the root with imported settings, remove unknowns"
    )
    argparser.add_argument(
        "-y", "--yes", action="store_true",
        help="Do not ask for confirmation"
    )
    argparser.add_argument(
        "-v", "--verbose", action="store_true",
        help="Verbose output"
    )
    args = argparser.parse_args()

    xion = Xion(xq=args.xq_path, verbose=args.verbose)
    if args.export:
        channel, root, output = args.export
        tree = xion.build_tree(channel, root)
        if tree is None:
            print("Failed to build config tree.")
            exit(1)
        success = xion.export_tree(channel, root, tree, output)
        exit(0 if success else 1)
    elif args.import_tree:
        channel, root, tree = xion.import_tree(args.import_tree)
        if channel and root and tree:
            force = bool(args.yes)
            replace = bool(args.replace)
            success = xion.apply_tree(channel, root, tree,
                                      confirm=not force, replace=replace)
            exit(0 if success else 1)
        else:
            print("Import failed.")
            exit(1)
    exit(0)


if __name__ == "__main__":
    main()
