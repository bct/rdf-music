import RDF

storage = RDF.HashStorage('music', options="hash-type='bdb',bulk='no'")
model = RDF.Model(storage)

def state(s, p, o):
  model.append(RDF.Statement(s, p, o))

def forget(s, p, o):
  '''delete all statements matching the given s, p, o (None matches anything)'''
  for st in model.find_statements(RDF.Statement(s, p, o)):
    del model[st]
