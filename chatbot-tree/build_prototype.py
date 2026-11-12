import json,sys
tree=json.load(open(sys.argv[1],encoding='utf-8'))
tpl=open(sys.argv[2],encoding='utf-8').read()
j=json.dumps(tree,ensure_ascii=False).replace("</","<\\/")
assert "/*TREE_JSON*/" in tpl
open(sys.argv[3],'w',encoding='utf-8').write(tpl.replace("/*TREE_JSON*/",j))
print("ok",len(j))
