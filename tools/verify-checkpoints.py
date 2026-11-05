#!/usr/bin/env python3
"""Verify exact red/green contracts in immutable Git checkpoint worktrees."""
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "target/checkpoint-checks"
TESTS = Path("src/test/java/com/juliendubois/workshop")
STAGES = ("start", "bugfix", "feature", "performance")


def activate(project, name):
    shutil.copyfile(project / "teaching" / f"{name}.java", project / TESTS / f"{name}.java")


def check(project, names, expected_tests, expected_failures=None):
    expected_failures = expected_failures or {}
    log = OUTPUT / f"{project.name}-{'-'.join(names)}.log"
    with log.open("w") as stream:
        result = subprocess.run(
            ["./mvnw", "-q", f"-Dtest={','.join(names)}", "test"],
            cwd=project, stdout=stream, stderr=subprocess.STDOUT, check=False)
    tests = errors = skipped = 0
    failures = {}
    for name in names:
        report = project / "target/surefire-reports" / f"TEST-com.juliendubois.workshop.{name}.xml"
        if not report.exists():
            raise RuntimeError(f"Missing test report; see {log}")
        suite = ET.parse(report).getroot()
        tests += int(suite.attrib["tests"])
        errors += int(suite.attrib["errors"])
        skipped += int(suite.attrib["skipped"])
        for case in suite.findall("testcase"):
            failure = case.find("failure")
            if failure is not None:
                if failure.attrib.get("type") != "org.opentest4j.AssertionFailedError":
                    raise RuntimeError(f"Not an intended assertion failure; see {log}")
                failures[f"{name}.{case.attrib['name']}"] = failure.attrib.get("message", "")
    if (tests, errors, skipped) != (expected_tests, 0, 0) or failures.keys() != expected_failures.keys():
        raise RuntimeError(f"{project.name}: unexpected result; see {log}")
    for name, fragments in expected_failures.items():
        if not all(fragment in failures[name] for fragment in fragments):
            raise RuntimeError(f"{name}: wrong assertion failed; see {log}")
    if (result.returncode == 0) != (len(expected_failures) == 0):
        raise RuntimeError(f"{project.name}: unexpected Maven exit; see {log}")
    print(f"{project.name}: {tests} executed, {len(failures)} intended assertion failures, no errors/skips", flush=True)
    return {"checkpoint": project.name, "tests": tests, "expectedAssertionFailures": list(failures)}


def git(*args):
    return subprocess.check_output(["git", "-C", str(ROOT), *args], text=True).strip()


def main():
    OUTPUT.mkdir(parents=True, exist_ok=True)
    checks = []
    revisions = {}
    with tempfile.TemporaryDirectory(prefix="cart-checkpoints-") as directory:
        projects = {}
        try:
            for stage in STAGES:
                tag = f"v1-{stage}"
                revision = git("rev-parse", f"{tag}^{{commit}}")
                project = Path(directory) / tag
                subprocess.run(["git", "-C", str(ROOT), "worktree", "add", "--detach",
                                str(project), revision], check=True, stdout=subprocess.DEVNULL)
                projects[stage] = project
                revisions[tag] = revision
                provenance = json.loads((project / ".github/skills/provenance.json").read_text())
                for name, digest in provenance["sha256"].items():
                    if hashlib.sha256((project / ".github/skills" / name).read_bytes()).hexdigest() != digest:
                        raise RuntimeError(f"Skill provenance mismatch: {tag}/{name}")
                for name in ("CartContractTest", "RemoveContractTest", "QueryContractTest"):
                    activated = project / TESTS / f"{name}.java"
                    if activated.exists() and activated.read_bytes() != (project / "teaching" / f"{name}.java").read_bytes():
                        raise RuntimeError(f"Acceptance test changed: {tag}/{name}")

            start, fixed, feature, optimized = (projects[stage] for stage in STAGES)
            checks.append(check(start, ["BaselineTest"], 4))
            activate(start, "CartContractTest")
            checks.append(check(start, ["CartContractTest"], 3, {
                "CartContractTest.repeatedAddIncrementsQuantityAndTotal": ("expected: 2", "but was: 1"),
                "CartContractTest.addingSeveralUnitsKeepsOneLine": ("expected: 5000", "but was: 2000"),
            }))
            checks.append(check(fixed, ["BaselineTest", "CartContractTest"], 7))
            activate(fixed, "RemoveContractTest")
            checks.append(check(fixed, ["RemoveContractTest"], 3, {
                "RemoveContractTest.removingTheLastItemReturnsAnEmptyCart": ("expected: 200", "but was: 404"),
                "RemoveContractTest.removingOneProductPreservesOtherLinesAndTotals": ("expected: 200", "but was: 404"),
            }))
            combined = ["BaselineTest", "CartContractTest", "RemoveContractTest"]
            checks.append(check(feature, combined, 10))
            activate(feature, "QueryContractTest")
            checks.append(check(feature, ["QueryContractTest"], 2, {
                "QueryContractTest.eightDistinctProductsUseOneSelect": ("expected: 1", "but was: 9"),
                "QueryContractTest.doublingTheCartDoesNotGrowTheSelectBudget": ("expected: 1", "but was: 17"),
            }))
            checks.append(check(optimized, combined + ["QueryContractTest"], 12))
        finally:
            for project in projects.values():
                subprocess.run(["git", "-C", str(ROOT), "worktree", "remove", "--force", str(project)], check=True)
    (OUTPUT / "manifest.json").write_text(json.dumps({
        "edition": "v1", "revisions": revisions, "checks": checks
    }, indent=2) + "\n")


if __name__ == "__main__":
    main()
