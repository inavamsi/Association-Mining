import rdflib

g = rdflib.Graph()
g.parse("hpo_ontology.owl")
g.bind('rdfs', 'http://www.w3.org/2000/01/rdf-schema#')
g.bind('oboInOwl', 'http://www.geneontology.org/formats/oboInOwl#')

qres = g.query(
    """SELECT ?sub ?obj ?namea ?nameb
       WHERE {
          ?sub rdfs:subClassOf ?obj .
          ?sub rdfs:label ?namea .
          ?obj rdfs:label ?nameb . 
       }""")

hpo=[]

for sub,obj,namea,nameb in qres:
    hpo.append(namea)
    hpo.append(nameb)

fo=open("all_hpo.txt",'w+')
for i in hpo:
    fo.write(i+'\n')
