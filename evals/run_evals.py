from __future__ import annotations
import json, sys
from pathlib import Path


def contains_clause(extracted, key):
    return bool((extracted or {}).get(key, '').strip())

def main():
    cases = json.loads(Path('evals/cases.json').read_text(encoding='utf-8'))
    results = {
        'total': 0,
        'passed': 0,
        'failed': 0,
        'failures': []
    }

    # Placeholder for future `analyze_text(text) -> Dict` function
    # analyze = None
    
    #try:

    #    from src.app.analyze import analyze_text
    #    analyze = analyze_text

    #except Exception:
    #    print('Eval harness ready, but `src.app.analyze.analyze_text not found.')
    #    print('Create it to run evals end-to-end')
    #    sys.exit(1)

    for c in cases:
        results['total'] += 1
        out = analyze(c['contract_text'])
        ok = True

        for k in c.get('must_include', []):
            if not contains_clause(out.get('extracted_classes'), k):
                ok = False
        
        exp = c.get('expect_risk_level')

        if exp and (out.get('risk_summary', {}).get('risk_level') != exp):
            ok = False

        if ok:
            results['passed'] += 1
        else:
            results['failed'] += 1
            results['failures'].append({ 'id': c['id'], 'out': out })

    print(json.dumps(results, indent=2))
    

if __name__ == '__main__':
    main()
    