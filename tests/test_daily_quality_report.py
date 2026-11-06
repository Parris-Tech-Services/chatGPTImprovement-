"""Daily GitHub/HTTP evidence summary: adversarial tests use zero real network calls."""
import json
import sys
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import daily_quality_report as q


def sample_run(name, branch="main", conclusion="success", event="push", when="2026-10-30T01:00:00Z", workflow=1):
    return {"name": name, "workflow_id": workflow, "head_branch": branch,
            "event": event, "conclusion": conclusion, "status": "completed",
            "head_sha": "f"*40, "html_url": "/actions/runs/1",
            "created_at": when}


class DailyQualityTests(unittest.TestCase):
    def test_old_green_does_not_verify_current_head(self):
        rows = q.latest_main_workflows([sample_run('Build')], 'main', 'a'*40)
        self.assertEqual(rows[0]['state'], 'PASS')
        self.assertEqual(rows[0]['current_head_state'], 'UNKNOWN')
        self.assertFalse(rows[0]['matches_default_head'])

    def test_matching_head_preserves_failure(self):
        rows = q.latest_main_workflows([sample_run('Build', conclusion='failure')], 'main', 'f'*40)
        self.assertEqual(rows[0]['current_head_state'], 'FAIL')

    def test_missing_head_cannot_claim_current_pass(self):
        rows = q.latest_main_workflows([sample_run('Build')], 'main')
        self.assertEqual(rows[0]['current_head_state'], 'UNKNOWN')

    def test_failing_pr_does_not_masquerade_as_failing_main(self):
        runs = [sample_run("Build", "feature", "failure", "pull_request", workflow=1),
                sample_run("Build", "main", "success", workflow=1)]
        report = q.latest_main_workflows(runs, "main")
        self.assertEqual(len(report), 1)
        self.assertEqual(report[0]["state"], "PASS")

    def test_latest_main_failure_is_not_hidden_by_older_green(self):
        runs = [sample_run("Build", "main", "failure", when="2026-10-30T02:00:00Z"),
                sample_run("Build", "main", "success", when="2026-10-30T01:00:00Z")]
        self.assertEqual(q.latest_main_workflows(runs,"main")[0]["state"],"FAIL")

    def test_pending_is_unknown_not_accepted_as_pass(self):
        run = sample_run("Build")
        run["conclusion"] = None
        run["status"] = "in_progress"
        self.assertEqual(q.latest_main_workflows([run],"main")[0]["state"],"UNKNOWN")

    def test_different_workflows_are_distinct(self):
        runs = [sample_run("Build", workflow=1),
                sample_run("Deploy", "main", "failure", workflow=2)]
        self.assertEqual({x["state"] for x in q.latest_main_workflows(runs,"main")}, {"PASS","FAIL"})

    def test_status_denominators_and_unknown_are_not_fabricated(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root/"docs/evidence").mkdir(parents=True)
            csv = root/"docs/MASTER_ACTION_BACKLOG_2026-10-29.csv"
            csv.write_text("id,status\nG01,VERIFIED COMPLETE\nG02,OPEN\n", encoding="utf-8")
            s=q.local_scorecard(root)
            self.assertEqual((s["registered_tasks"],s["claimed_complete"],s["open_tasks"]), (2,1,1))
            self.assertEqual(s["recorded_valid_complete"],0)
            self.assertEqual(s["unsupported_register_claims"],["G01"])
            self.assertIn("UNKNOWN",s["daily_task_completion_rate"])

    def test_missing_records_do_not_claim_zero_rework(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);(root/"docs/evidence").mkdir(parents=True)
            (root/"docs/MASTER_ACTION_BACKLOG_2026-10-29.csv").write_text(
                "id,status\nG01,OPEN\n",encoding="utf-8")
            s=q.local_scorecard(root)
            self.assertEqual(s["measured_rework"]["value"],"UNKNOWN")
            self.assertEqual(s["measured_claim_verification"]["value"],"UNKNOWN")

    def test_duplicate_register_id_fails_closed(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"register.csv"
            p.write_text("id,status\nG01,OPEN\nG01,OPEN\n",encoding="utf-8")
            with self.assertRaises(ValueError):q.read_register(p)

    def test_remote_api_failure_is_unknown(self):
        with patch.object(q,"request_json",side_effect=OSError("API down")):
            result=q.remote_project("Parris-Tech-Services/FaithHub",
                 datetime(2026,10,30,2,tzinfo=timezone.utc))
        self.assertEqual(result["state"],"UNKNOWN")

    def test_real_api_shaped_data_projects_main_only(self):
        responses=[
            {"private":False,"default_branch":"main"},
            {"commit":{"sha":"f"*40}},
            {"workflow_runs":[sample_run("Build","main","success"),sample_run("Build","feature","failure","pull_request")]},
            [{"number":4},{"number":5}],
        ]
        with patch.object(q,"request_json",side_effect=responses):
            p=q.remote_project("Parris-Tech-Services/FaithHub",
                datetime(2026,10,30,2,tzinfo=timezone.utc))
        self.assertEqual((p["state"],p["open_pr_count"],p["last_24h_main_runs"]),("OBSERVED",2,1))
        self.assertEqual(p["last_24h_failed_main_runs"],0)
        self.assertEqual(p["latest_main_workflows"][0]["state"],"PASS")
        self.assertEqual(p["latest_main_workflows"][0]["current_head_state"],"PASS")

    def test_private_repo_is_not_queried_further(self):
        with patch.object(q,"request_json",return_value={"private":True}) as f:
            p=q.remote_project("example/private",datetime.now(timezone.utc))
        self.assertEqual(f.call_count,1)
        self.assertEqual(p["state"],"SKIPPED_PRIVATE")

    def test_page_failure_not_pass_from_http_200_without_marker(self):
        class Response:
            status=200
            url="https://parris-tech-services.github.io/FaithHub/"
            def read(self,_):return b"<html>No expected app heading</html>"
            def __enter__(self):return self
            def __exit__(self,*_):return None
        with patch.object(q.urllib.request,"urlopen",return_value=Response()):
            s=q.check_public_page(q.SITE_CHECKS["FaithHub home"])
        self.assertEqual(s["state"],"FAIL")


    def test_town_release_mismatch_fails_even_if_host_is_ready(self):
        class Response:
            status = 200
            def read(self, _): return json.dumps({"sourceCommit": "a"*40}).encode()
            def __enter__(self): return self
            def __exit__(self, *_): return None
        projects = [{"repo": q.TOWN_REPO, "state": "OBSERVED", "default_head_sha": "b"*40}]
        with patch.object(q.urllib.request, "urlopen", return_value=Response()) as request:
            result = q.check_town_production_release(projects)
        self.assertEqual(result["state"], "FAIL")
        self.assertEqual(result["live_source_sha"], "a"*40)
        self.assertEqual(request.call_args.args[0].full_url, q.TOWN_RELEASE_URL)
        self.assertNotIn("Authorization", dict(request.call_args.args[0].header_items()))

    def test_town_release_equal_sha_passes_version_parity_only(self):
        class Response:
            status = 200
            def read(self, _): return json.dumps({"sourceCommit": "a"*40}).encode()
            def __enter__(self): return self
            def __exit__(self, *_): return None
        with patch.object(q.urllib.request, "urlopen", return_value=Response()):
            result = q.check_town_production_release([
                {"repo": q.TOWN_REPO, "state": "OBSERVED", "default_head_sha": "a"*40}])
        self.assertEqual(result["state"], "PASS")
        self.assertIn("not a browser playtest", result["meaning"])

    def test_town_release_missing_main_does_not_claim_success_or_network(self):
        with patch.object(q.urllib.request, "urlopen",
                          side_effect=AssertionError("must not try network")):
            self.assertEqual(q.check_town_production_release([])["state"], "UNKNOWN")

    def test_town_release_non_object_json_is_unknown(self):
        class Response:
            status = 200
            def read(self, _): return b"[]"
            def __enter__(self): return self
            def __exit__(self, *_): return None
        with patch.object(q.urllib.request, "urlopen", return_value=Response()):
            result = q.check_town_production_release([
                {"repo": q.TOWN_REPO, "state": "OBSERVED", "default_head_sha": "a"*40}])
        self.assertEqual(result["state"], "UNKNOWN")

    def test_town_release_unreadable_manifest_is_unknown(self):
        with patch.object(q.urllib.request, "urlopen", side_effect=OSError("protected")):
            result = q.check_town_production_release([
                {"repo": q.TOWN_REPO, "state": "OBSERVED", "default_head_sha": "a"*40}])
        self.assertEqual(result["state"], "UNKNOWN")

    def test_strict_report_rejects_proven_stale_town_production(self):
        with tempfile.TemporaryDirectory() as d:
            report = {"red_latest_main_workflows_repos": [], "live_http_checks": {},
                      "production_release_checks": {"Repository Town production": {"state": "FAIL"}}}
            with (
                patch.object(q, "build_report", return_value=report),
                patch.object(q, "as_markdown", return_value="Stale production"),
            ):
                self.assertEqual(q.main(["--strict", "--out", d]), 1)

    def test_offline_run_never_networks_or_claims_daily_task_metrics(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);(root/"docs/evidence").mkdir(parents=True)
            (root/"docs/MASTER_ACTION_BACKLOG_2026-10-29.csv").write_text(
                "id,status\nG01,OPEN\n",encoding="utf-8")
            with patch.object(q,"request_json",side_effect=AssertionError("no network")):
                out=q.build_report(root,datetime(2026,10,30,0,tzinfo=timezone.utc),True)
            self.assertEqual(out["public_projects"],[])
            self.assertEqual(out["live_http_checks"],{})
            self.assertEqual(out["production_release_checks"],{})
            self.assertIn("UNKNOWN",q.as_markdown(out))

if __name__ == "__main__":
    unittest.main()
