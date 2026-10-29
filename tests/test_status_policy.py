"""Negative acceptance suite for G01; offline checker is NOT a real attestor."""
import copy
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from check_task_record import digest_contract, validate


def good(user_facing=True, status='VERIFIED COMPLETE'):
    kinds = ['artifact', 'test'] + (['live'] if user_facing else [])
    criteria = [{'id':f'AC-{i+1}', 'kind':kind, 'description':f'Prove {kind} outcome'} for i,kind in enumerate(kinds)]
    evidence = [{'id':f'E-{i+1}', 'kind':kind, 'reference':f'https://example.test/evidence/{i}',
                 'observed_by':'independent-reviewer', 'provenance':'external_observed'} for i,kind in enumerate(kinds)]
    data={
        'schema_version':1,'task_id':'G01','task_type':'software' if user_facing else 'documentation',
        'user_facing':user_facing,'actor':'agent-under-review','status':status,
        'contract':{'user_outcome':'Publish an independently checked, working outcome', 'criteria':criteria,'digest_sha256':''},
        'results':[{'criterion_id':c['id'],'outcome':'PASS','evidence_ids':[e['id']]} for c,e in zip(criteria,evidence)],
        'evidence':evidence,'external_actions':[], 'remaining_work':[], 'blocker':None,
    }
    data['contract']['digest_sha256']=digest_contract(data)
    return data

class StatusPolicyTests(unittest.TestCase):
    def assertBad(self,data,needle):
        msgs=validate(data)
        self.assertTrue(any(needle in s for s in msgs),f'Expected {needle!r}, got {msgs}')

    def test_valid_software_live_complete(self):self.assertEqual(validate(good()),[])
    def test_valid_documentation_no_live(self):self.assertEqual(validate(good(False)),[])
    def test_missing_live_criterion(self):
        data=good();data['contract']['criteria']=[c for c in data['contract']['criteria'] if c['kind']!='live'];
        data['contract']['digest_sha256']=digest_contract(data)
        self.assertBad(data,'must include live acceptance')
    def test_live_unverified_blocks_complete(self):
        data=good();data['results'][-1]['outcome']='NOT_RUN';self.assertBad(data,'requires PASS for AC-3')
    def test_live_self_report_blocks_complete(self):
        data=good();data['evidence'][-1]['provenance']='self_reported';self.assertBad(data,'independent evidence of matching kind for AC-3')
    def test_imported_transcript_blocks_complete(self):
        data=good();data['evidence'][-1]['provenance']='transcript_imported';self.assertBad(data,'independent evidence')
    def test_agent_self_review_blocks_complete(self):
        data=good();data['evidence'][-1]['observed_by']='agent-under-review';self.assertBad(data,'independent evidence')
    def test_missing_or_wrong_evidence_kind(self):
        data=good();data['evidence'][-1]['kind']='test';self.assertBad(data,'matching kind for AC-3')
    def test_changed_acceptance_fails_digest(self):
        data=good();data['contract']['criteria'][0]['description']='Weakened goal';self.assertBad(data,'digest mismatch')
    def test_sha_does_not_authenticate_consent(self):
        data=good();data['contract']['criteria'][0]['description']='Changed and restamped';data['contract']['digest_sha256']=digest_contract(data)
        self.assertEqual(validate(data),[],'Self-restamping must remain possible; cryptographic anchoring belongs to AgentWitness')
    def test_missing_result(self):
        data=good();data['results'].pop();self.assertBad(data,'one result per criterion')
    def test_unknown_evidence(self):
        data=good();data['results'][-1]['evidence_ids']=['unknown'];self.assertBad(data,'unknown evidence')
    def test_duplicate_criterion(self):
        data=good();data['contract']['criteria'][1]['id']='AC-1';data['contract']['digest_sha256']=digest_contract(data);self.assertBad(data,'duplicate criterion')
    def test_duplicate_evidence(self):
        data=good();data['evidence'][1]['id']='E-1';self.assertBad(data,'duplicate evidence')
    def test_complete_with_remaining_work_rejected(self):
        data=good();data['remaining_work']=['Browser still broken'];self.assertBad(data,'cannot have remaining')
    def test_complete_with_blocker_rejected(self):
        data=good();data['blocker']={'reason':'No browser'};self.assertBad(data,'cannot have remaining')
    def test_email_send_without_approval_rejected(self):
        data=good();data['external_actions']=[{'action':'email_send','performed':True,'approval_reference':'','approval_scope':'email_send'}]
        self.assertBad(data,'missing approval')
    def test_broad_email_approval_rejected(self):
        data=good();data['external_actions']=[{'action':'email_forward','performed':True,'approval_reference':'explicit-ref','approval_scope':'general_assistance'}]
        self.assertBad(data,'send-specific')
    def test_valid_send_specific_approval_metadata(self):
        data=good();data['external_actions']=[{'action':'email_send','performed':True,'approval_reference':'explicit-ref','approval_scope':'email_send'}]
        self.assertEqual(validate(data),[])
    def test_deploy_without_approval_rejected(self):
        data=good();data['external_actions']=[{'action':'deploy','performed':True,'approval_reference':'','approval_scope':''}]
        self.assertBad(data,'missing approval')
    def test_partial_requires_remaining_and_some_work(self):
        data=good();data['status']='PARTIALLY COMPLETE';data['results']=[];data['evidence']=[]
        self.assertBad(data,'must name remaining work');self.assertBad(data,'needs some recorded work')
    def test_all_not_run_cannot_count_as_partial(self):
        data=good();data['status']='PARTIALLY COMPLETE';data['evidence']=[];data['remaining_work']=['Everything']
        for result in data['results']:
            result['outcome']='NOT_RUN';result['evidence_ids']=[]
        self.assertBad(data,'needs some recorded work/evidence')
    def test_malformed_nested_provenance_does_not_crash(self):
        data=good();data['evidence'][-1]['provenance']=[]
        self.assertBad(data,'evidence must have')
        self.assertBad(data,'requires independent evidence')
    def test_invalid_utf8_returns_input_error(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'bad.json';p.write_bytes(b'\\xff')
            proc=subprocess.run([sys.executable,str(ROOT/'scripts/check_task_record.py'),str(p)],capture_output=True,text=True)
            self.assertEqual(proc.returncode,2,proc.stdout)
            self.assertIn('INVALID RECORD',proc.stderr)
    def test_valid_partial(self):
        data=good();data['status']='PARTIALLY COMPLETE';data['results'][-1]['outcome']='NOT_RUN';data['remaining_work']=['Live acceptance outstanding']
        self.assertEqual(validate(data),[])
    def test_blocked_requires_reason_attempts_next_action(self):
        data=good();data['status']='BLOCKED';self.assertBad(data,'BLOCKED requires')
    def test_valid_blocked(self):
        data=good();data['status']='BLOCKED';data['blocker']={'reason':'Tool inaccessible','attempted_alternatives':'Checked local executable and connector','next_action':'Authorised runner needed'}
        self.assertEqual(validate(data),[])
    def test_not_started_cannot_claim_evidence(self):
        data=good();data['status']='NOT STARTED';self.assertBad(data,'cannot claim actions')
    def test_valid_not_started(self):
        data=good();data['status']='NOT STARTED';data['results']=[];data['evidence']=[]
        self.assertEqual(validate(data),[])
    def test_cancelled_reason_required(self):
        data=good();data['status']='CANCELLED';self.assertBad(data,'CANCELLED requires reason')
    def test_valid_cancelled(self):
        data=good();data['status']='CANCELLED';data['blocker']={'reason':'User cancelled'}
        self.assertEqual(validate(data),[])
    def test_duplicate_result_rejected(self):
        data=good();data['results'].append(copy.deepcopy(data['results'][0]));self.assertBad(data,'duplicate criterion results')
    def test_malformed_fields_do_not_crash(self):
        # Fail closed for untrusted JSON, including non-hashable values.
        mutations=[('status',[]),('task_type',[]),('schema_version',True),('schema_version',1.0),('user_facing','false')]
        for key,value in mutations:
            data=good();data[key]=value
            with self.subTest(key=key):
                try: e=validate(data)
                except Exception as ex:self.fail(f'Unexpected exception: {ex}')
                self.assertTrue(e)
    def test_non_object_fails(self):self.assertTrue(validate([]))
    def test_cli_valid_and_invalid_exit(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'evidence.json';p.write_text(json.dumps(good()))
            proc=subprocess.run([sys.executable,str(ROOT/'scripts/check_task_record.py'),str(p)],capture_output=True,text=True)
            self.assertEqual(proc.returncode,0,proc.stderr)
            self.assertIn('NOT AN INDEPENDENT ATTESTATION',proc.stdout)
            bad=good();bad['results'][-1]['outcome']='NOT_RUN';p.write_text(json.dumps(bad))
            proc=subprocess.run([sys.executable,str(ROOT/'scripts/check_task_record.py'),str(p)],capture_output=True,text=True)
            self.assertEqual(proc.returncode,1,proc.stdout)

if __name__ == '__main__':unittest.main()
