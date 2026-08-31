#!/usr/bin/env python3
import argparse
import json
from pathlib import Path

from build_staging_workflow import build as build_v1, sha256_file


def node_by_name(wf, name):
    matches=[n for n in wf['nodes'] if n.get('name')==name]
    if len(matches)!=1:
        raise RuntimeError(f'expected one node {name!r}, found {len(matches)}')
    return matches[0]


def build():
    wf=build_v1()
    wf['name']='SPM WU103 Knowledge Maintenance STAGING Candidate'

    # Read full shadow history so interrupted two-step UPDATE publication can be
    # deterministically repaired on retry. Canonical family reads remain ACTIVE-only.
    shadow_read=node_by_name(wf,'Load WU103 KB Shadow [STAGING]')
    shadow_read['parameters'].pop('filtersUI',None)

    decision=node_by_name(wf,'Build WU103 Publish Decisions')
    js=decision['parameters']['jsCode']

    marker="if(clean(r.regression_payload_sha256)!==clean(r.candidate_payload_sha256))reasons.push('REGRESSION_PAYLOAD_HASH_MISMATCH');\n if(type!=='ADD'&&type!=='UPDATE')reasons.push('INVALID_CHANGE_TYPE');"
    replacement="""if(clean(r.regression_payload_sha256)!==clean(r.candidate_payload_sha256))reasons.push('REGRESSION_PAYLOAD_HASH_MISMATCH');
 const regCases=arr(r.regression_case_ids);
 if(!/^[a-f0-9]{64}$/.test(clean(r.regression_evidence_sha256)))reasons.push('REGRESSION_EVIDENCE_REQUIRED');
 if(new Set(regCases).size<2)reasons.push('REGRESSION_CASES_INCOMPLETE');
 if(!['WEBSITE','ATTACHMENT','QUALITY_NOTE','OWNER_DECISION','INTERNAL_APPROVED_SOURCE'].includes(clean(r.source_type)))reasons.push('SOURCE_TYPE_REQUIRED');
 if(!clean(r.source_reference))reasons.push('SOURCE_REFERENCE_REQUIRED');
 if(arr(r.language_scope).length<1)reasons.push('LANGUAGE_SCOPE_REQUIRED');
 if(type!=='ADD'&&type!=='UPDATE')reasons.push('INVALID_CHANGE_TYPE');"""
    if marker not in js:
        raise RuntimeError('regression marker not found')
    js=js.replace(marker,replacement)

    js=js.replace(
        "let logicalId=null,baseRevision=null,baseFp=null,supersede=null;",
        "let logicalId=null,baseRevision=null,baseFp=null,supersede=null,idempotentExisting=null;",
    )

    start=js.find(" } else if(a&&type==='UPDATE'){")
    end=js.find("\n }\n const allowed=",start)
    if start<0 or end<0:
        raise RuntimeError('UPDATE decision block not found')
    update_block=r''' } else if(a&&type==='UPDATE'){
   logicalId=clean(r.target_record_id);
   const allForId=shadow.filter(x=>clean(x.target_family)===family&&clean(x.logical_record_id)===logicalId);
   const activeShadow=allForId.filter(x=>clean(x.record_status)==='ACTIVE');
   const sameCurrent=activeShadow.filter(x=>clean(x.change_id)===clean(r.change_id)&&clean(x.payload_sha256)===payloadSha&&clean(x.revision)===clean(r.candidate_revision));
   if(activeShadow.length===1&&sameCurrent.length===1){
     const cur=sameCurrent[0]; idempotentExisting=cur;
     if(clean(cur.source_queue_event_id)!==clean(r.source_queue_event_id))reasons.push('CHANGE_ID_PROVENANCE_MISMATCH');
     if(clean(cur.base_fingerprint_sha256)!==clean(r.base_fingerprint_sha256))reasons.push('STALE_BASE_RECORD');
     if(/^v\d+$/.test(clean(r.base_revision))){const prev=allForId.filter(x=>clean(x.record_status)==='SUPERSEDED'&&clean(x.revision)===clean(r.base_revision));if(prev.length===1)supersede=prev[0];}
   } else if(activeShadow.length===2&&sameCurrent.length===1){
     const cur=sameCurrent[0]; const old=activeShadow.find(x=>x!==cur); idempotentExisting=cur; supersede=old;
     baseRevision=clean(old.revision); baseFp=clean(old.payload_sha256);
     if(clean(r.base_revision)!==baseRevision)reasons.push('STALE_BASE_REVISION');
     if(clean(r.base_fingerprint_sha256)!==baseFp)reasons.push('STALE_BASE_RECORD');
     const next=/^v\d+$/.test(baseRevision)?`v${Number(baseRevision.slice(1))+1}`:null;
     if(next&&clean(r.candidate_revision)!==next)reasons.push('CANDIDATE_REVISION_MISMATCH');
     if(clean(cur.base_fingerprint_sha256)!==baseFp||clean(cur.supersedes_revision)!==baseRevision)reasons.push('INTERRUPTED_PUBLISH_LINEAGE_MISMATCH');
   } else if(activeShadow.length>1){
     reasons.push('BASE_RECORD_NOT_UNIQUE');
   } else if(activeShadow.length===1){
     const b=activeShadow[0]; baseRevision=clean(b.revision); baseFp=clean(b.payload_sha256); supersede=b;
     if(clean(r.base_revision)!==baseRevision)reasons.push('STALE_BASE_REVISION');
     if(clean(r.base_fingerprint_sha256)!==baseFp)reasons.push('STALE_BASE_RECORD');
     const next=/^v\d+$/.test(baseRevision)?`v${Number(baseRevision.slice(1))+1}`:null;
     if(next&&clean(r.candidate_revision)!==next)reasons.push('CANDIDATE_REVISION_MISMATCH');
   } else {
     const matches=canonical[family].filter(x=>clean(x[a.id])===logicalId&&clean(x.status).toUpperCase()==='ACTIVE');
     if(matches.length!==1)reasons.push('BASE_RECORD_NOT_UNIQUE');
     else {const norm={};for(const f of a.fields)if(f!=='last_reviewed')norm[f]=matches[0][f];baseRevision='LEGACY_UNVERSIONED';baseFp=sha256(canonical(norm));}
     if(baseRevision&&clean(r.base_revision)!==baseRevision)reasons.push('STALE_BASE_REVISION');
     if(baseFp&&clean(r.base_fingerprint_sha256)!==baseFp)reasons.push('STALE_BASE_RECORD');
     if(clean(r.candidate_revision)!=='v1')reasons.push('CANDIDATE_REVISION_MISMATCH');
   }'''
    js=js[:start]+update_block+js[end:]

    old_new="const allowed=reasons.length===0; const newShadow=allowed?{target_family:family,logical_record_id:logicalId,revision:clean(r.candidate_revision),change_id:clean(r.change_id),source_queue_event_id:clean(r.source_queue_event_id),payload_json:payloadCanonical,payload_sha256:payloadSha,base_fingerprint_sha256:baseFp||'',record_status:'ACTIVE',published_at:now,supersedes_revision:supersede?clean(supersede.revision):''}:null;\n const ledgerUpdate=allowed?{...r,updated_at:now,change_state:'PUBLISHED',publish_status:'PUBLISHED',published_at:now,published_record_id:logicalId,published_payload_sha256:payloadSha,supersedes_change_id:supersede?clean(supersede.change_id):clean(r.supersedes_change_id)}:null;"
    new_new="""const allowed=reasons.length===0;
 const newShadow=allowed?(idempotentExisting?{...idempotentExisting}:{target_family:family,logical_record_id:logicalId,revision:clean(r.candidate_revision),change_id:clean(r.change_id),source_queue_event_id:clean(r.source_queue_event_id),payload_json:payloadCanonical,payload_sha256:payloadSha,base_fingerprint_sha256:baseFp||'',record_status:'ACTIVE',published_at:now,supersedes_revision:supersede?clean(supersede.revision):''}):null;
 const publishTs=idempotentExisting?(clean(idempotentExisting.published_at)||now):now;
 const ledgerUpdate=allowed?{...r,updated_at:now,change_state:'PUBLISHED',publish_status:'PUBLISHED',published_at:publishTs,published_record_id:logicalId,published_payload_sha256:payloadSha,supersedes_change_id:supersede?clean(supersede.change_id):clean(r.supersedes_change_id)}:null;"""
    if old_new not in js:
        raise RuntimeError('new-shadow marker not found')
    js=js.replace(old_new,new_new)
    decision['parameters']['jsCode']=js

    prepare=node_by_name(wf,'Prepare WU103 Shadow Writes')
    prepare['parameters']['jsCode']=r'''const out=[]; for(const i of $input.all()){const d=i.json||{}; if(d.wu103_publish_allowed!==true)continue; if(d.new_shadow_row)out.push({json:d.new_shadow_row}); if(d.supersede_shadow_row)out.push({json:d.supersede_shadow_row});} return out;'''
    return wf


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--output',required=True);args=ap.parse_args()
    wf=build();out=Path(args.output);out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(wf,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'output':str(out),'sha256':sha256_file(out),'nodes':len(wf['nodes']),'connections':len(wf['connections']),'active':wf['active'],'hardening':'evidence+retry-recovery'},indent=2))

if __name__=='__main__':main()
