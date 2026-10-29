"""Build the Czech practice modules and add Czech prompts to Velo, straight into gym/.
Usage (from gym/src): python build_cz.py
  - ../czgram.js   Czech grammar (cz_grammar.py)
  - ../czvocab.js  Czech vocabulary (cz_vocab.py)
  - ../velo.js     adds q.cz (velo_cz.py) to the existing Velo module; build.py does the same on a full rebuild."""
import json, os
import cz_grammar, cz_vocab, velo_cz

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')

def write(name, data):
    with open(os.path.join(OUT, name + '.js'), 'w', encoding='utf-8') as f:
        f.write('export default ' + json.dumps(data, ensure_ascii=False) + ';\n')
    print(name, len(data['questions']), 'items')

write('czgram', dict(id='czgram', kind='cz', name='Čeština · gramatika', tagline='Czech grammar A1: lesson + drills per topic',
                     schema=[], notes=[], questions=cz_grammar.questions()))
write('czvocab', dict(id='czvocab', kind='cz', name='Čeština · slovíčka', tagline='Czech vocabulary for work with data',
                      schema=[], notes=[], questions=cz_vocab.questions()))

p = os.path.join(OUT, 'velo.js')
s = open(p, encoding='utf-8').read()
data = json.loads(s[len('export default '):].rstrip().rstrip(';'))
assert len(data['questions']) == len(velo_cz.CZ)
for i, q in enumerate(data['questions'], 1):
    q['cz'] = velo_cz.CZ[i]
with open(p, 'w', encoding='utf-8') as f:
    f.write('export default ' + json.dumps(data, ensure_ascii=False) + ';\n')
print('velo: Czech prompts added to', len(data['questions']), 'questions')
