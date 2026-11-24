import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys

use = Path(sys.argv[1]).resolve()
out = Path(sys.argv[2]).resolve()
spec = importlib.util.spec_from_file_location('checker',use/'use-plugin/tools/verify-state-checker.py')
checker = importlib.util.module_from_spec(spec)
spec.loader.exec_module(checker)
module = use/'use-plugin/target'
cp = os.pathsep.join((str(module/'classes'), (module/'runtime-classpath.txt').read_text().strip()))
models = checker.MODELS

for case in sys.argv[3:]:
    path = out/case
    project = path/'project'
    checker.prepare(case, project)
    plan = project/checker.ASL
    original = plan.read_text()
    if case == 'missing_property':
        updated = checker.replace_one(original, '!verification_start(Sch); !verification_after_start.',
                                      '!verification_start(Sch); .send(alice,tell,verification_start_boundary); !verification_after_start.')
    else:
        updated = checker.replace_one(original, '!verification_one_bid(AId,10); !verification_after_bid_1;',
                                      '!verification_one_bid(AId,10); .send(bob,tell,verification_bid_first); !verification_after_bid_1;')
        updated = checker.replace_one(updated, '!verification_one_bid(AId,20); !verification_after_bid_2.',
                                      '!verification_one_bid(AId,20); .send(bob,tell,verification_bid_second); !verification_after_bid_2.')
    plan.write_text(updated)
    import difflib
    (path/'boundary.diff').write_text(''.join(difflib.unified_diff(original.splitlines(True),updated.splitlines(True),
                                        fromfile='original-instrumented.asl',tofile='handoff-instrumented.asl')))
    work = path/'run'
    work.mkdir()
    command = ['java', '-Duse.state.work='+str(work), '-cp', cp,
               'org.tzi.use.plugins.jacamo.entrypoint.WorkbenchMain',
               str(project/'auction.jcm'), str(models/'attribute-mapping.xml'), str(models/'auction.csl'),
               str(models/'auction.istar'), '--headless', '--seconds=8']
    with (path/'console.log').open('w') as log:
        run = subprocess.run(command, cwd=use, stdout=log, stderr=subprocess.STDOUT, timeout=55)
    (work/'bridge-secret.hex').unlink(missing_ok=True)
    rows = checker.records(work)
    result = checker.evaluate(*next(c for c in checker.CASES if c[0]==case),project,work,rows,run.returncode)
    result['run'] = rows[0]['request']['run']
    result['operatorCheckpoints'] = []
    for row in rows:
        r,s = row['request'],row['response']
        seq = r['snapshot']['sequence']
        if r['checkpoint']['boundary']=='AGENT_HANDOFF' or s['decision']!='APPROVE':
            result['operatorCheckpoints'].append({
                'seq':seq,'agent':r.get('agent'),'boundary':r['checkpoint']['boundary'],
                'complete':r['snapshot']['complete'],'decision':s['decision'],'diagnostic':s.get('diagnostic'),
                'auctionValues':[[a['name'],a['properties'].get('best_bid')] for a in r['snapshot']['artifacts'] if a['name'] in ('a1','a2')],
                'invariants': sorted({(c['id'],c['verdict']) for c in s.get('result',{}).get('checks',[]) if c['kind']=='CSL_INVARIANT'}),
                'receiptMatches':json.loads((work/f'checkpoint-{seq}.json').read_text())==row,
            })
    if 'firstHoldSequence' in result and result['firstHoldSequence'] is not None:
        hold=result['firstHoldSequence']
        prev=next((r for r in rows if r['request']['snapshot']['sequence']==hold-1),None)
        if prev:
            result['snapshotBeforeHold'] = [[a['name'],a['properties'].get('best_bid')] for a in prev['request']['snapshot']['artifacts'] if a['name'] in ('a1','a2')]
    (path/'result.json').write_text(json.dumps(result,indent=2)+'\n')
    print(case, result['classification'],result['checkpoints'],result['firstHoldSequence'],result['run'],flush=True)
