import difflib,gzip,importlib.util,json,os,pathlib,shutil,sys
root=pathlib.Path.cwd()
e=pathlib.Path(os.environ["THESIS_EVIDENCE"])
archived=pathlib.Path(os.environ["THESIS_CASES"])
sys.dont_write_bytecode=True
def module(name,file):
 spec=importlib.util.spec_from_file_location(name,root/file)
 obj=importlib.util.module_from_spec(spec);spec.loader.exec_module(obj);return obj
checker=module("checker","use-plugin/tools/verify-state-checker.py")
pack=module("pack","use-plugin/tools/pack-mrv.py")
def end(project,base):
 return pack.pack(project/(base+".jcm"),project/"attribute-mapping.xml",project/(base+".csl"),project/(base+".istar"),[])
def existing(case,base):
 folder=e/case; folder.mkdir(exist_ok=True);return folder,folder/"project"
def norm(text): return text.replace("\r\n","\n").replace("\\","/")
for label,mutation in (("TN05-loi-chuyen-giao","increasing_best_bid"),("TN06-thieu-chuyen-giao","missing_property")):
 folder,project=existing(label,"auction")
 archived_case=archived/label
 checker.prepare(mutation,project)
 generated=(folder/"mutation.diff").read_text()
 history=gzip.decompress((archived_case/"mutation.diff.gz").read_bytes()).decode()
 assert norm(generated)==norm(history),label
 script=project/checker.ASL
 old=script.read_text(encoding="utf8")
 if mutation=="missing_property":
  new=checker.replace_one(old,'!verification_start(Sch); !verification_after_start.',
      '!verification_start(Sch); .send(alice,tell,verification_start_boundary); !verification_after_start.')
 else:
  new=checker.replace_one(old,'!verification_one_bid(AId,10); !verification_after_bid_1;',
      '!verification_one_bid(AId,10); .send(bob,tell,verification_bid_first); !verification_after_bid_1;')
  new=checker.replace_one(new,'!verification_one_bid(AId,20); !verification_after_bid_2.',
      '!verification_one_bid(AId,20); .send(bob,tell,verification_bid_second); !verification_after_bid_2.')
 boundary=''.join(difflib.unified_diff(old.splitlines(True),new.splitlines(True),fromfile='original-instrumented.asl',tofile='handoff-instrumented.asl'))
 assert norm(boundary)==norm(gzip.decompress((archived_case/"boundary.diff.gz").read_bytes()).decode()),label
 script.write_text(new,encoding="utf8")
 (folder/"boundary.diff").write_text(boundary,encoding="utf8")
 for name in ("auction.istar","auction.csl","attribute-mapping.xml"):
  shutil.copy2(checker.MODELS/name,project/name)
 print(end(project,"auction"))
for label in ("TN07-counter-giu-am","TN07-counter-khoi-phuc"):
 folder,project=existing(label,"counter")
 shutil.copytree(checker.EXAMPLE.parent/"counter",project,ignore=shutil.ignore_patterns("*.mrv"))
 shutil.copy2(archived/label/"Counter.java",project/"src/env/state_demo/Counter.java")
 shutil.copy2(archived/label/"counter.asl",project/"src/agt/counter.asl")
 print(end(project,"counter"))

