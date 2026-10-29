"""G04 adversarial tests: inflated successes, hidden exclusions, double counting and missing data
must never improve the reported KPIs; every aggregate reconciles to task IDs."""
import copy
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
sys.path.insert(0, str(ROOT / 'tests'))
from kpi_ledger import UNKNOWN, compute
from test_status_policy import good


def rec(tid, status='VERIFIED COMPLETE', user_facing=False, **kpi):
    r = good(user_facing, status) if status == 'VERIFIED COMPLETE' else good(user_facing)
    r['task_id'] = tid
    from check_task_record import digest_contract
    if status != 'VERIFIED COMPLETE':
        r['status'] = status
        r['remaining_work'] = ['finish it'] if status == 'PARTIALLY COMPLETE' else []
        if status == 'BLOCKED':
            r['blocker'] = {'reason': 'no access', 'attempted_alternatives': 'asked', 'next_action': 'grant access'}
    r['contract']['digest_sha256'] = digest_contract(r)
    r['kpi'] = {'eligible': True, **kpi}
    return (tid + '.json', r)


class KpiLedgerTests(unittest.TestCase):
    def test_success_reconciles_to_ids(self):
        rep = compute([rec('T1'), rec('T2', 'PARTIALLY COMPLETE'), rec('T3', 'BLOCKED')])
        s = rep['kpis']['end_to_end_task_success']
        self.assertEqual((s['numerator'], s['denominator'], s['numerator_ids']), (1, 3, ['T1']))
        self.assertEqual(s['denominator_ids'], ['T1', 'T2', 'T3'])

    def test_inflated_verified_is_not_success(self):
        _, bad = rec('T1'); bad['evidence'][0]['provenance'] = 'self_reported'   # no independent proof
        rep = compute([('T1.json', bad), rec('T2')])
        self.assertEqual(rep['kpis']['end_to_end_task_success']['numerator_ids'], ['T2'])
        self.assertEqual(rep['kpis']['status_inflation_ids'], ['T1'])
        self.assertEqual(rep['kpis']['status_accuracy']['value'], 0.5)

    def test_tampered_scope_is_not_success(self):
        _, r = rec('T1'); r['contract']['criteria'] = r['contract']['criteria'][:1]   # criteria cut after freezing
        r['results'] = r['results'][:1]
        rep = compute([('T1.json', r)])
        self.assertEqual(rep['kpis']['end_to_end_task_success']['numerator'], 0)

    def test_exclusion_needs_reason_and_is_listed(self):
        rep = compute([rec('T1'), rec('T2', 'BLOCKED', eligible=False)])
        self.assertTrue(any('excluded without a reason' in e for e in rep['errors']))
        self.assertEqual(rep['kpis']['end_to_end_task_success']['denominator'], 2, 'reasonless exclusion must stay in')
        rep = compute([rec('T1'), rec('T2', 'BLOCKED', eligible=False, excluded_reason='user cancelled')])
        self.assertEqual(rep['excluded'], [{'task_id': 'T2', 'reason': 'user cancelled'}])
        self.assertEqual(rep['kpis']['end_to_end_task_success']['denominator'], 1)

    def test_unknown_eligibility_stays_in_denominator(self):
        n, r = rec('T2', 'BLOCKED'); del r['kpi']
        rep = compute([rec('T1'), (n, r)])
        self.assertEqual(rep['kpis']['end_to_end_task_success']['denominator'], 2)
        self.assertEqual(rep['eligibility_unknown_ids'], ['T2'])

    def test_duplicates_are_not_double_counted(self):
        # Two records for one task: neither is trusted, so neither counts (and the run fails).
        rep = compute([rec('T1'), rec('T1'), rec('T1')])
        self.assertTrue(any('duplicate' in e for e in rep['errors']))
        self.assertEqual(rep['kpis']['end_to_end_task_success']['numerator'], 0)
        self.assertEqual(rep['record_count'], 0)

    def test_missing_data_is_unknown_not_zero(self):
        rep = compute([rec('T1')])
        k = rep['kpis']
        self.assertEqual(k['assistant_caused_rework']['value'], UNKNOWN)
        self.assertEqual(k['assistant_caused_rework']['missing_ids'], ['T1'])
        self.assertEqual(k['corrective_followups_per_task']['value'], UNKNOWN)
        self.assertEqual(k['claim_verification']['value'], UNKNOWN)
        self.assertEqual(k['delivery_lead_time_hours_median']['value'], UNKNOWN)
        self.assertEqual(compute([])['kpis']['end_to_end_task_success']['value'], UNKNOWN)

    def test_measured_values(self):
        rep = compute([rec('T1', assistant_rework=True, corrective_followups=2, claims_made=4, claims_supported=3,
                           accepted_at='2026-10-29T01:00:00Z', verified_at='2026-10-29T05:00:00Z'),
                       rec('T2', assistant_rework=False, corrective_followups=0, claims_made=2, claims_supported=2,
                           accepted_at='2026-10-29T01:00:00Z', verified_at='2026-10-29T03:00:00Z')])
        k = rep['kpis']
        self.assertEqual(k['assistant_caused_rework']['value'], 0.5)
        self.assertEqual(k['corrective_followups_per_task']['value'], 1.0)
        self.assertEqual(k['claim_verification']['value'], round(5 / 6, 4))
        self.assertEqual(k['delivery_lead_time_hours_median']['value'], 3.0)

    def test_impossible_claim_counts_are_rejected(self):
        rep = compute([rec('T1', claims_made=1, claims_supported=5)])
        self.assertEqual(rep['kpis']['claim_verification']['value'], UNKNOWN)

    def test_unauthorised_action_counted(self):
        n, r = rec('T1')
        r['external_actions'] = [{'action': 'merge', 'performed': True}]
        rep = compute([(n, r)])
        self.assertEqual(rep['kpis']['unauthorised_actions']['count'], 1)
        self.assertEqual(rep['kpis']['end_to_end_task_success']['numerator'], 0, 'record with unapproved action is invalid')

    def test_register_claim_without_record(self):
        rep = compute([rec('T1')], register=[{'id': 'T1', 'status': 'VERIFIED COMPLETE'}, {'id': 'T9', 'status': 'VERIFIED COMPLETE'},
                                             {'id': 'T5', 'status': 'OPEN'}])
        self.assertEqual(rep['register_unsupported_verified_claims'], ['T9'])


class ReviewRegressionTests(unittest.TestCase):
    def test_claims_from_invalid_records_do_not_count(self):
        n, r = rec('T1', claims_made=100, claims_supported=100)
        r['evidence'][0]['provenance'] = 'self_reported'
        rep = compute([(n, r), rec('T2', claims_made=2, claims_supported=1)])
        self.assertEqual(rep['kpis']['claim_verification']['value'], 0.5)
        self.assertIn('T1', rep['kpis']['claim_verification']['missing_ids'])

    def test_mixed_timezones_are_missing_not_a_crash(self):
        rep = compute([rec('T1', accepted_at='2026-10-29T01:00:00', verified_at='2026-10-29T05:00:00Z')])
        self.assertEqual(rep['kpis']['delivery_lead_time_hours_median']['value'], UNKNOWN)
        self.assertEqual(rep['kpis']['delivery_lead_time_hours_median']['missing_ids'], ['T1'])

    def test_wrong_scope_or_blank_approval_is_unauthorised(self):
        for action in [{'action': 'email_send', 'performed': True, 'approval_reference': 'chat-1', 'approval_scope': 'email_reply'},
                       {'action': 'merge', 'performed': True, 'approval_reference': '  ', 'approval_scope': 'merge'}]:
            n, r = rec('T1'); r['external_actions'] = [action]
            self.assertEqual(compute([(n, r)])['kpis']['unauthorised_actions']['count'], 1, action)

    def test_malformed_records_do_not_stop_the_report(self):
        n, r = rec('T2'); r['external_actions'] = 7
        rep = compute([('null.json', None), ('num.json', 3), ('t.json', True), (n, r), rec('T1')])
        self.assertEqual(sum('unreadable' in e for e in rep['errors']), 3)
        self.assertEqual(rep['kpis']['end_to_end_task_success']['numerator_ids'], ['T1'])

    def test_totals_trace_back_to_tasks(self):
        rep = compute([rec('T1', corrective_followups=2, claims_made=3, claims_supported=3,
                           accepted_at='2026-10-29T01:00:00Z', verified_at='2026-10-29T02:30:00Z')])
        k = rep['kpis']
        self.assertEqual(k['corrective_followups_per_task']['per_task'], {'T1': 2})
        self.assertEqual(k['claim_verification']['per_task'], {'T1': [3, 3]})
        self.assertEqual(k['delivery_lead_time_hours_median']['per_task'], {'T1': 1.5})


if __name__ == '__main__':
    unittest.main()
