"""Check that specs for all modules are present
"""
import os
import re
import sys
import yaml

SPLITTER = re.compile(r'([^ %]+)(?: ?(%[^ ]+))?')


def run():
    """Run a module check
    """
    try:
        module_fn, spec_fn = sys.argv[1:]
    except ValueError:
        msg = "usage: {0} modules.yaml specs.txt"
        print(msg.format(os.path.basename(sys.argv[0])))
        sys.exit(1)

    with open(module_fn) as fd:
        modules = yaml.load(fd) \
                      .get('modules', {}) \
                      .get('tcl', {}) \
                      .get('whitelist', [])

    with open(spec_fn) as fd:
        specs = [l.strip() for l in fd]

    missing = []
    for module in modules:
        requirements = [g for g in SPLITTER.match(module).groups() if g]

        def fits(reqs, parts):
            for r in reqs:
                matches = [p for p in parts if p.startswith(r)]
                if len(matches) == 0:
                    return False
                parts.remove(matches[0])
            return True

        for spec in specs:
            if fits(requirements, spec.split()):
                break
        else:
            missing.append(module)

    if missing:
        with open("missing.txt", "a") as fd:
            fd.writelines("{0}\n".format(m) for m in missing)


if __name__ == '__main__':
    run()
