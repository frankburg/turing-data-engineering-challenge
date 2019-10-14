import json
with open('results01.json', 'r') as js:
    data1=json.load(i)
    
with open('results02.json', 'r') as js:
    data2=json.load(i)

with open('results03.json', 'r') as js:
    data3=json.load(i)
    
res=data1.extend(data2)
result=res.extend(data3)

with open('results.json','w') as f:
        json.dump(result,f)