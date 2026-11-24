import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

use = Path(sys.argv[1]).resolve()
out = Path(sys.argv[2]).resolve()
source = use / 'use-plugin/src/main/resources/example/counter'
module = use / 'use-plugin/target'
cp = os.pathsep.join((str(module/'classes'), (module/'runtime-classpath.txt').read_text().strip()))

for case, restored in [('counter_persistent', False), ('counter_restored', True)]:
    folder = out / case
    folder.mkdir(parents=True)
    project = shutil.copytree(source, folder/'project')
    artifact = project/'src/env/state_demo/Counter.java'
    code = artifact.read_text()
    hook = 'getObsProperty("value").updateValue(value);'
    assert code.count(hook) == 1
    artifact.write_text(code.replace(hook, hook+'System.out.println("COUNTER_WITNESS value="+value);'))
    if restored:
        plan = project/'src/agt/counter.asl'
        text = plan.read_text()
        orig = '!reach_target; !invalid.'
        assert text.count(orig)==1
        plan.write_text(text.replace(orig, '!reach_target; !invalid; !restore.').replace(
            '+!invalid <- set(-1).', '+!invalid <- set(-1).\n+!restore <- set(2).'))
    run_out = folder/'run'
    with (folder/'console.log').open('w') as log:
        subprocess.run(['java', '-Duse.state.work='+str(run_out), '-cp', cp,
                        'org.tzi.use.plugins.jacamo.entrypoint.WorkbenchMain',
                        str(project/'counter.jcm'), str(project/'attribute-mapping.xml'),
                        str(project/'counter.csl'), str(project/'counter.istar'),
                        '--headless','--seconds=8'], cwd=use, stdout=log, stderr=subprocess.STDOUT,
                       check=True, timeout=55)
    (run_out/'bridge-secret.hex').unlink(missing_ok=True)
    trace = [json.loads(line) for line in (run_out/'consumer-history.jsonl').read_text().splitlines()]
    last = trace[-1]
    result = {
        'run': last['request']['run'],
        'sequence':last['request']['snapshot']['sequence'],
        'boundary':last['request']['checkpoint']['boundary'],
        'mergedPlans':last['request']['checkpoint']['mergedPlans'],
        'snapshotValues':[
            [row['request']['snapshot']['sequence'],
             [a['properties']['value'] for a in row['request']['snapshot']['artifacts'] if a['name']=='counter']]
            for row in trace],
        'decision':last['response']['decision'],
        'checks':[(c['id'],c['verdict']) for c in last['response']['result']['checks'] if c['id'].endswith('Nonnegative')],
        'witness':[line.split('COUNTER_WITNESS value=', 1)[1].strip()
                   for line in (run_out/'producer.log').read_text().splitlines() if 'COUNTER_WITNESS value=' in line],
    }
    receipt = json.loads((run_out/('checkpoint-'+str(result['sequence'])+'.json')).read_text())
    assert last==receipt
    assert result['decision']==('APPROVE' if restored else 'HOLD_FAILURE'), result
    assert result['witness'] == (['0','1','2','-1','2'] if restored else ['0','1','2','-1']),result
    (folder/'result.json').write_text(json.dumps(result,indent=2)+'\n')
    print(case,json.dumps(result),flush=True)
