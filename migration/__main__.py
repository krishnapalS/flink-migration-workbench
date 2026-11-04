import argparse,json,sys
from pathlib import Path
from .compiler import write_artifacts,Rejected
from .powercenter import read_export

def main():
    p=argparse.ArgumentParser(description='Compile a strict bounded mapping; never deploys.')
    p.add_argument('input',type=Path);p.add_argument('--out',type=Path,default=Path('build'))
    args=p.parse_args()
    try:
        ir=read_export(args.input) if args.input.suffix=='.xml' else json.loads(args.input.read_text())
        manifest=write_artifacts(ir,args.out)
    except (Rejected,ValueError,TypeError,KeyError,OSError) as e:
        print('REJECTED: '+str(e),file=sys.stderr);return 2
    print(json.dumps(manifest,indent=2));return 0
if __name__=='__main__':sys.exit(main())
