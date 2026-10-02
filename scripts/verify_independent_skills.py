from pathlib import Path
import json
from release import hashes,validate
ROOT=Path(__file__).resolve().parents[1]
def main():
 m=validate();lock=json.loads((ROOT/'independent-skills-lock.json').read_text())
 assert {x['name'] for x in m['skills']}==set(lock['skills'])
 for row in m['skills']:
  assert hashes(ROOT/'skills'/row['name'])==lock['skills'][row['name']]['files'],row['name']
 print('PASS canonical independent payloads:',len(m['skills']))
if __name__=='__main__':main()
