from __future__ import print_function
from subprocess import check_output
import json
import warnings
import os
import sys

NOHASH = "<no hash_input.json in file>"
BASEKEY = "BASE"


try:
    check_output('conda')
    AVAILABLE = True
except OSError:
    warnings.warn("Executing outside CONDA environment.")
    AVAILABLE = False


class CondaError(Exception):
    pass


class CondaNotFound(CondaError):
    pass


def call_conda(cmd, *args):
    if not AVAILABLE:
        raise CondaNotFound()
    return check_output(['conda', cmd] + list(args))


def _parse_json_out(output):
    try:
        data = output.strip()
        # Cleaning from extra dirty data
        while data and data[-1] != '}':
            data = data[:-1]
        return json.loads(data)
    except ValueError as ve:
        raise CondaError("Invalid JSON response cause {}:\n{}".format(ve, output))


def call_conda_json(cmd, *args):
    out = call_conda(cmd, '--json', *args)
    if not out:
        raise CondaError("No output")
    return _parse_json_out(out)


def conda_inspect_hash(packpath):
    out = call_conda('inspect', 'hash-inputs', packpath)
    if not out:
        raise CondaError("No output")
    data = out.strip()
    # Cleaning from extra dirty data
    while data and data[-1] != '}':
        data = data[:-1]
    return eval(data)


def collect_variants_reqs(distropath):
    allhash = dict()
    allreqs = dict()
    for fname in os.listdir(distropath):
        if not fname.endswith(".tar.bz2"):
            continue
        fullname = os.path.join(distropath, fname)
        hashh = conda_inspect_hash(fullname)
        print("=== {} ===\n{}".format(fname, json.dumps(hashh, sort_keys=True, indent=2)))
        allhash.update(hashh)
        for pname, content in hashh.items():
            if not isinstance(content, dict) and content == NOHASH:
                continue
            recipe = content.get("recipe", {})
            if not recipe:
                continue
            for rkey, reqs in recipe.items():
                if rkey == "requirements":
                    for key, detreqs in reqs.items():
                        allreqs.setdefault(key, set())
                        allreqs[key] |= set(detreqs)
                        print('{}: {}'.format(key, sorted(detreqs)))
                elif rkey == 'build':
                    runexkey = "run_exports"
                    if reqs.get(runexkey):
                        allreqs.setdefault(runexkey, set())
                        allreqs[runexkey] |= set(reqs[runexkey])
                elif rkey not in ("source", "extra"):
                    allreqs.setdefault(BASEKEY, set()).add('{} {}'.format(rkey, reqs))
    return {key: sorted(val) for key, val in allreqs.items()}, allhash


def distro_report(distropath):
    for distrovariant in os.listdir(distropath):
        distrovariant = os.path.join(distropath, distrovariant)
        if not os.path.isdir(distrovariant):
            continue
        areqs, ahash = collect_variants_reqs(distrovariant)
        for what, fname in ((ahash, "allhashes.json"), (areqs, "allreqs.json")):
            if not what:
                break
            fullname = os.path.join(distrovariant, fname)
            print("Writing {}".format(fullname))
            with open(fullname, "w") as outf:
                json.dump(what, outf, sort_keys=True, indent=2)


if __name__ == '__main__':
    where = os.path.abspath(sys.argv[1])
    if not os.path.isdir(where):
        raise RuntimeError("Invalid path {}".format(where))
    distro_report(where)
