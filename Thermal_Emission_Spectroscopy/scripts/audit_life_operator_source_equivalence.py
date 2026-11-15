"""Verify the full-run operator despite later documentation-only edits.

Reverse exactly the recorded documentation/error-text patch. The reconstructed
source must match the archived full-run SHA-256 byte for byte. Then compare
Python ASTs after removing docstrings and normalizing only the two error
messages, so changed executable calculations cannot pass this provenance gate.
"""

import ast
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PROJECT = ROOT / "Thermal_Emission_Spectroscopy/outputs/life_proxima_b_earthlike_v1"
CAMPAIGN = PROJECT / "retrievals/a0_fixed_reference_A3_1000h_binning_corrected_20261015"
BASELINE = PROJECT / "retrievals/a3_1000h_binning_corrected_20261014"
SOURCE = Path(__file__).with_name("life_bin_operator_diagnostic.py")
REPLACEMENTS = [
    ('"""LIFE generator-compatible energy-flux observation operator.',
     '"""Isolated LIFE generator-compatible energy-flux observation operator.'),
    ("it is not a newly calibrated instrumental response. A process-local binding\n"
     "lets tests and explicitly scoped retrieval wrappers use the same entry point\n"
     "as POSEIDON's forward model.",
     "it is not a newly calibrated instrumental response. A process-local binding\n"
     "allows diagnostics to use the same entry point as POSEIDON's forward model."),
    ("LIFE operator requires its frozen native grid",
     "Diagnostic operator requires its frozen native grid"),
    ("LIFE binding accepts only one LIFE dataset",
     "Diagnostic binding accepts only one LIFE dataset"),
    ("    Used by operator tests and the explicitly scoped corrected-retrieval\n"
     "    wrapper. The wrapper keeps this binding active through sampling and\n"
     "    posterior postprocessing. The optional module permits a dependency-free\n"
     "    unit test of restoration, including exceptions.",
     "    For diagnostics only. No MultiNest run is dispatched. The optional module\n"
     "    permits a dependency-free unit test of restoration, including exceptions."),
]


def digest(blob):
    return hashlib.sha256(blob).hexdigest()


class NormalizeDocumentation(ast.NodeTransformer):
    def visit_Constant(self, node):
        messages = dict(REPLACEMENTS[2:4])
        if isinstance(node.value, str):
            inverse = {value: key for key, value in messages.items()}
            node.value = inverse.get(node.value, node.value)
        return node

    def generic_visit(self, node):
        super().generic_visit(node)
        if isinstance(node, (ast.Module, ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            if (node.body and isinstance(node.body[0], ast.Expr)
                    and isinstance(node.body[0].value, ast.Constant)
                    and isinstance(node.body[0].value.value, str)):
                node.body = node.body[1:]
        return node


def audit(write=False):
    snapshot = json.loads((BASELINE / "preserved_inputs.json").read_text())
    expected = snapshot[str(SOURCE.relative_to(ROOT)).replace("\\", "/")]
    blob = SOURCE.read_bytes()
    current = blob.decode("utf-8")
    reconstructed = current.replace("\r\n", "\n")
    for after, before in REPLACEMENTS:
        if reconstructed.count(after) != 1:
            raise ValueError("Recorded documentation patch does not match current source")
        reconstructed = reconstructed.replace(after, before)
    candidates = [reconstructed.encode("utf-8"),
                  reconstructed.replace("\n", "\r\n").encode("utf-8")]
    original = next((candidate for candidate in candidates if digest(candidate) == expected), None)
    if original is None:
        raise ValueError("Reconstructed source does not match the full-run checksum")
    original_ast = ast.dump(NormalizeDocumentation().visit(ast.parse(original)), include_attributes=False)
    current_ast = ast.dump(NormalizeDocumentation().visit(ast.parse(current)), include_attributes=False)
    if original_ast != current_ast:
        raise ValueError("Executable operator AST changed beyond the documented error messages")
    record = {
        "status": "PASS", "full_run_source_sha256": expected,
        "current_source_sha256": digest(blob),
        "reconstructed_source_sha256": digest(original),
        "executable_AST_equal_except_docstrings_and_two_error_messages": True,
        "normalised_AST_sha256": digest(current_ast.encode("utf-8")),
        "changes": "module/function documentation and two ValueError descriptions only",
        "scientific_operator_change": False,
    }
    if write:
        directory = CAMPAIGN / "source_equivalence"
        directory.mkdir(exist_ok=True)
        source_copy = directory / "life_bin_operator_at_full_launch.py"
        if source_copy.exists() and source_copy.read_bytes() != original:
            raise ValueError("Existing reconstructed source differs; preserve it")
        if not source_copy.exists():
            source_copy.write_bytes(original)
        (directory / "audit.json").write_text(json.dumps(record, indent=2) + "\n")
    return record


if __name__ == "__main__":
    print(json.dumps(audit(write=True), indent=2))
