"""Validate the bounded White Paper release; never alter source data or gates."""
from pathlib import Path
import csv,json,re,hashlib,subprocess,zipfile
from decimal import Decimal as D
import fitz
from docx import Document
ROOT=Path(__file__).parent;REPO=ROOT.parents[1];BASE='5c0fdb60eede8a5bb0e7ede9fd551ad4e3b65fb2'
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def rows(p):
 with (REPO/p).open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
checks=[]
def check(ok,label):
 if not ok:raise AssertionError(label)
 checks.append(label)
manifest=json.loads((ROOT/'analysis/input_manifest.json').read_text())
for p,h in manifest['sources'].items():check(digest(REPO/p)==h,'source_hash:'+p)
ref=json.loads((REPO/'data/current_research_reference.json').read_text())
check(ref['reference_version']=='13.0','reference_version')
check(digest(REPO/ref['reference_path'])==ref['reference_sha256'],'reference_payload')
check(set(ref['live_use_gates'].values())=={'BLOCKED_FOR_LIVE_USE'},'both_gates_closed')
md=(ROOT/'whitepaper.md').read_text();check(digest(ROOT/'whitepaper.md')=='114be4b5957e9a1caf87b7c9edd1005fde0cb732919f05642c5fc12af32bdcce','exact_locally_reviewed_manuscript')
check(len(re.findall(r'^!\[Figure \d+\.',md,re.M))==19,'nineteen_captioned_figures')
check(len(re.findall(r'^\[\d+\] \*\*',md,re.M))==20,'twenty_reference_groups')
check('turn'+'file' not in md and '' not in md,'no_tool_tokens')
extra=['data/public_deliverable_crosswalk_2027.csv','data/deliverable_training_comparison.csv','data/ga_unmiss_abolishments.csv','data/census_v10/product_obligations.csv','data/census_v13/affected_recheck.csv']
tr={r['output_pair_id']:r for r in rows(extra[0])}
for key,a,b in [('TR01','150','360'),('TR02','150','136'),('TR03','150','50'),('TR04','150','312')]:
 check((tr[key]['planned_2027_a'],tr[key]['planned_2027_b'],tr[key]['count_unit'])==(a,b,'days'),'training_units:'+key)
cs=[r for r in rows('data/ga_approved_resource_components.csv') if r['hierarchy']=='maintenance_top_level']
ga=rows('data/ga_mission_reconciliation.csv')
for cat,key in [('military_police','ga_approved_military_police_usd_thousands'),('civilian_personnel','ga_approved_civilian_usd_thousands'),('operational_requirements','ga_approved_operational_usd_thousands')]:
 check(sum(D(r['approved_usd_thousands']) for r in cs if r['component']==cat)==sum(D(r[key]) for r in ga),'independent_category_sum:'+cat)
check(len(rows('data/census_v10/product_obligations.csv'))==61,'fixed_denominator')
check(len(rows('data/census_v13/affected_recheck.csv'))==2,'affected_recheck_not_whole_score')
for extension in ['png','svg']:check(len(list((ROOT/'figures').glob('*.'+extension)))==19,'figure_count:'+extension)
docx=ROOT/'deliverables/UN_Peace_Operations_White_Paper_2026-10-15.docx';pdf=docx.with_suffix('.pdf')
d=Document(docx);check(len(d.inline_shapes)==19,'docx_embedded_figures')
with zipfile.ZipFile(docx) as z:check(z.testzip() is None,'docx_zip_integrity')
p=fitz.open(pdf);check(len(p)==32,'pdf_32_pages')
alltext='\n'.join(q.get_text() for q in p)
for i,q in enumerate(p,1):check(len(q.get_text().strip())>100,'nonempty_pdf_page:'+str(i))
for n in range(1,20):check('Figure '+str(n)+'.' in alltext,'pdf_caption:'+str(n))
for entry in json.loads((ROOT/'analysis/planned_pages.json').read_text()):
 text=p[entry['planned_page']-1].get_text()
 check(re.sub(r'\s+','',entry['title']) in re.sub(r'\s+','',text),'heading_on_expected_page:'+str(entry['planned_page'])+':'+entry['title'])
# LibreOffice can list the same shared resource dictionary on every page.
# Count unique PDF image objects, not repeated resource references.
check(len({image[0] for page in p for image in page.get_images()})==19,'pdf_unique_embedded_figures')
files=subprocess.check_output(['git','ls-tree','-r','--name-only',BASE],cwd=REPO,text=True).splitlines()
for name in files:
 before=subprocess.check_output(['git','show',BASE+':'+name],cwd=REPO)
 check((REPO/name).is_file() and (REPO/name).read_bytes()==before,'preserved:'+name)
check(not any(x.suffix.lower() in {'.ttf','.otf','.woff','.woff2'} for x in ROOT.rglob('*')),'no_font_files')
record=dict(status='PASS_document_data_layout_structure_and_preservation_not_operational_validation',baseline_commit=BASE,pages=32,figures=19,reference_groups=20,checks_passed=len(checks),source_manifest_inputs=len(manifest['sources']),additional_source_hashes={x:digest(REPO/x) for x in extra},preexisting_tracked_files_preserved=len(files),reference_version='13.0',live_use='both_BLOCKED_FOR_LIVE_USE',rankings='unchanged',course_checks_run=0,new_staff_time_or_cash_savings='not_estimated',manuscript_sha256=digest(ROOT/'whitepaper.md'),output_hashes={str(x.relative_to(ROOT)):digest(x) for x in [docx,pdf,ROOT/'analysis/chart_data.json',ROOT/'analysis/functional_coverage.csv']},visual_review='32 local rendered pages inspected separately; automated checks are not visual review of a different runtime',limitations='Whole-project synthesis of retained source records. Not exhaustive operational census, fresh budget authorization, independent owner review or realized savings audit.')
(ROOT/'analysis/validation_receipt.json').write_text(json.dumps(record,indent=2)+'\n')
print(json.dumps(record,indent=2))
