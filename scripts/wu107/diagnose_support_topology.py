#!/usr/bin/env python3
import argparse, json
from pathlib import Path

GATEWAY='Deterministic Action Gateway [RC3 SCOPE LOCK]'
TELEMETRY='Build Telemetry Envelope'
KEYWORDS=('support','technical','complaint','handoff','escalat')

def targets(conn):
    out=[]
    for branch in conn.get('main',[]) if isinstance(conn,dict) else []:
        for edge in branch or []:
            out.append(edge.get('node'))
    return [x for x in out if x]

def main():
    p=argparse.ArgumentParser(); p.add_argument('--candidate',required=True); a=p.parse_args()
    d=json.loads(Path(a.candidate).read_text())
    conns=d.get('connections',{})
    nodes={n.get('name'):n for n in d.get('nodes',[])}

    incoming={name:[] for name in nodes}
    for src,conn in conns.items():
        for dst in targets(conn):
            incoming.setdefault(dst,[]).append(src)

    print('WU107_CR10701_TOPOLOGY_DIAGNOSTIC_BEGIN')
    print('gateway_incoming=',json.dumps(sorted(incoming.get(GATEWAY,[]))))
    print('gateway_outgoing=',json.dumps(targets(conns.get(GATEWAY,{}))))
    print('telemetry_incoming=',json.dumps(sorted(incoming.get(TELEMETRY,[]))))
    print('telemetry_outgoing=',json.dumps(targets(conns.get(TELEMETRY,{}))))

    relevant=[]
    for name,node in nodes.items():
        text=(name+' '+str(node.get('notes',''))+' '+json.dumps(node.get('parameters',{}),ensure_ascii=False)).lower()
        if any(k in text for k in KEYWORDS):
            relevant.append(name)
    print('support_related_nodes=',json.dumps(sorted(relevant),ensure_ascii=False))

    # Emit only topology around support-related nodes; never emit customer data or credentials.
    for name in sorted(relevant):
        print('NODE',json.dumps(name,ensure_ascii=False),
              'IN',json.dumps(sorted(incoming.get(name,[])),ensure_ascii=False),
              'OUT',json.dumps(targets(conns.get(name,{})),ensure_ascii=False))

    # Detect alternate paths that enter telemetry without traversing the gateway insertion.
    direct_to_telemetry=[x for x in incoming.get(TELEMETRY,[]) if x not in {
        'Apply WU107 Verified Queue Result','Apply WU107 Existing Handoff Result',
        'Build WU107 Handoff Load Failure Context','Build WU107 Handoff Save Failure Context',
        'Is WU107 Handoff Execution Required?'
    }]
    print('non_wu107_direct_telemetry_predecessors=',json.dumps(sorted(direct_to_telemetry),ensure_ascii=False))
    print('WU107_CR10701_TOPOLOGY_DIAGNOSTIC_END')

if __name__=='__main__': main()
