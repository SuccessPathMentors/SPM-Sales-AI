#!/usr/bin/env python3
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[1]
SPEC = importlib.util.spec_from_file_location("deploy_nonprod", HERE / "deploy_nonprod.py")
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(MODULE)


def sample_workflow():
    return {
        "id": "CMBMpxX5AqqK2UTn",
        "name": "Production Source",
        "active": True,
        "createdAt": "2026-08-30T00:00:00Z",
        "nodes": [
            {
                "id": "node-1",
                "name": "Start",
                "type": "n8n-nodes-base.manualTrigger",
                "typeVersion": 1,
                "position": [0, 0],
                "parameters": {},
            },
            {
                "id": "node-2",
                "name": "NoOp",
                "type": "n8n-nodes-base.noOp",
                "typeVersion": 1,
                "position": [200, 0],
                "parameters": {},
            },
        ],
        "connections": {
            "Start": {
                "main": [[{"node": "NoOp", "type": "main", "index": 0}]]
            }
        },
        "settings": {
            "executionOrder": "v1",
            "binaryMode": "separate",
            "credentialResolverId": "internal-only",
            "availableInMCP": True,
        },
    }


class NonProdSafetyTests(unittest.TestCase):
    def test_graph_validation_passes_valid_workflow(self):
        result = MODULE.validate_graph(sample_workflow())
        self.assertEqual(result["node_count"], 2)

    def test_graph_validation_rejects_unknown_target(self):
        wf = sample_workflow()
        wf["connections"]["Start"]["main"][0][0]["node"] = "Missing"
        with self.assertRaises(MODULE.SafetyError):
            MODULE.validate_graph(wf)

    def test_sanitizer_drops_server_and_internal_fields(self):
        payload = MODULE.sanitize_workflow(sample_workflow(), "staging")
        self.assertTrue(payload["name"].startswith("[STAGING] "))
        self.assertNotIn("id", payload)
        self.assertNotIn("active", payload)
        self.assertNotIn("createdAt", payload)
        self.assertNotIn("binaryMode", payload["settings"])
        self.assertNotIn("credentialResolverId", payload["settings"])
        self.assertFalse(payload["settings"]["availableInMCP"])

    def test_production_id_is_hard_denied(self):
        with self.assertRaises(MODULE.SafetyError):
            MODULE.assert_safe_target(
                {"name": "[STAGING] anything", "active": False},
                "CMBMpxX5AqqK2UTn",
                "staging",
            )

    def test_active_target_is_denied(self):
        with self.assertRaises(MODULE.SafetyError):
            MODULE.assert_safe_target(
                {"name": "[DEV] anything", "active": True},
                "dev-target-123",
                "dev",
            )

    def test_wrong_environment_prefix_is_denied(self):
        with self.assertRaises(MODULE.SafetyError):
            MODULE.assert_safe_target(
                {"name": "Production Source", "active": False},
                "dev-target-123",
                "dev",
            )

    def test_policy_matches_hardcoded_production_denylist(self):
        policy = json.loads(
            (REPO_ROOT / "n8n" / "deployment" / "nonprod-policy.json").read_text(
                encoding="utf-8"
            )
        )
        policy_ids = {x["id"] for x in policy["protected_production_workflows"]}
        self.assertEqual(policy_ids, MODULE.PROTECTED_PRODUCTION_WORKFLOW_IDS)

    def test_sha256_roundtrip(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "workflow.json"
            p.write_text(json.dumps(sample_workflow()), encoding="utf-8")
            raw, parsed = MODULE.load_json_bytes(p)
            self.assertEqual(parsed["name"], "Production Source")
            self.assertEqual(MODULE.sha256_bytes(raw), MODULE.sha256_bytes(p.read_bytes()))


if __name__ == "__main__":
    unittest.main(verbosity=2)
