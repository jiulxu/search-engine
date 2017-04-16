from flask import *
import requests
import math
import operator
import re

main = Blueprint('main', __name__, template_folder='templates')

inv_index={}
file1=open("output.txt",'r')
for line in file1:
    linelist=line.strip().split(" ")
    term=linelist[0]
    idf=linelist[1]
    inv_index[term]={"idf":idf,"docs":{}}
    for i in range(1,len(linelist)/3):
        inv_index[term]["docs"][linelist[3*i]]=(linelist[3*i+1],linelist[3*i+2])
file1.close()

page_rank={}
file2=open("pagerank.out",'r')
for line in file2:
    linelist=line.split(",")
    page_rank[linelist[0].strip()]=linelist[1].strip()
file2.close()

stop_words=[]
file3=open("stopwords.txt",'r')
for line in file3:
    word=line.strip()
    stop_words.append(word)
file3.close()

@main.route('/', methods = ['GET'])
def api_route():
    query = request.args.get('q')
    weight = float(request.args.get('w'))
    query_list=query.strip().split(" ")
    valid_dict={}
    for term in query_list:
        term=re.sub(r'[^a-zA-Z0-9]+', '', term)
        if not term == "":
            term=term.lower()
            if not term in stop_words:
                if term in valid_dict:
                    valid_dict[term]+=1
                else:
                    valid_dict[term]=1

    fail=False
    if len(valid_dict)==0:
        fail=True
    for term in valid_dict.keys():
        if not term in inv_index:
            fail=True

    Rsp={"hits":[]}
    print(valid_dict)

    if not fail:
        query_norm_fac=0
        for term in valid_dict.keys():
            idf=float(inv_index[term]["idf"])
            query_norm_fac+=idf*idf*valid_dict[term]*valid_dict[term]    

        valid_list=list(valid_dict.keys())
        result_list=list(inv_index[valid_list[0]]["docs"].keys())
        for i in range(1,len(valid_list)):
            cur_list=list(inv_index[valid_list[i]]["docs"].keys())
            result_list=list(set(result_list)&set(cur_list))

        scores={}
        for doc in result_list:
            scores[doc]=0

        for term in valid_list:
            cur_dict=inv_index[term]
            idf=float(cur_dict["idf"])
            for doc in result_list:
                tf=int(cur_dict["docs"][doc][0])
                normfac=float(cur_dict["docs"][doc][1])
                scores[doc]+=valid_dict[term]*idf*tf*idf/(math.sqrt(normfac)*math.sqrt(query_norm_fac))

        for doc in result_list:
            pgrk=0
            if doc in page_rank:
                pgrk=float(page_rank[doc])
            scores[doc]=weight*pgrk+(1-weight)*scores[doc]

        sorted_scores=sorted(scores.items(), key=operator.itemgetter(1))
        sorted_scores.reverse()

        i=1
        while i<len(sorted_scores):
            if sorted_scores[i][1]==sorted_scores[i-1][1] and sorted_scores[i][0]<sorted_scores[i-1][0]:
                save=sorted_scores[i]
                sorted_scores[i]=sorted_scores[i-1]
                sorted_scores[i-1]=save
                i-=1
            else: i+=1

        for doc in sorted_scores:
            Rsp["hits"].append({"docid":int(doc[0]),"score":doc[1]})

    return jsonify(Rsp)







