from pathlib import Path
import json,subprocess,sys,tempfile
ROOT=Path(__file__).resolve().parents[1]
def main():
 m=json.loads((ROOT/'skills-manifest.json').read_text())
 with tempfile.TemporaryDirectory() as temp:
  for row in m['skills']:
   if not row['entrypoint']:continue
   out=Path(temp)/(row['name']+'.'+row['format'])
   subprocess.run([sys.executable,str(ROOT/'skills'/row['name']/row['entrypoint']),'--example','--output',str(out)],cwd=temp,check=True)
   if row['name']=='tw-edu-exam-generator':assert out.with_name(out.stem+'-student.docx').exists()
   else:assert out.exists()
 print('PASS all manifest-selected independent generators')
if __name__=='__main__':main()
