import query
import scrape_url
import display
import sys
from gpt_extraction import url_fetch
from extract_relations_modified import extract_relations

needed_relation=['per:schools_attended', 'per:employee_of', 'per:cities_of_residence','org:top_members/employees']

# Take user input "", ""
print() 
method = sys.argv[1]    
googlekey = sys.argv[2]
enginekey = sys.argv[3]
openaikey = sys.argv[4]
r = int(sys.argv[5]) #1#3 #4
thresh = float(sys.argv[6]) #0.7
k = int(sys.argv[8]) #10#2 #10
q =sys.argv[7] #"mark zuckerberg harvard"#bill gates microsoft" #"sundar pichai google" #"megan repinoe redding" 

print()
print('-------- PARAMETERS ---------')
print("Client Key       = ", googlekey)
print("Engine Key       = ", enginekey)
print("OpenAI Key       = ", openaikey)
print("Method           = ", method)
print("Relation         = ", needed_relation[r-1])
print("Threshold        = ", thresh)
print("Query            = ", q)
print("Number of Tuples = ", k)
print('-----------------------------')
print("Loading necessary libraries; This should take a minute or so ...")

perfect_relations = []
seen_urls = []
used_queries = []

# Start iterating until k tuples are found.
iteration_number = 0
while len(perfect_relations) < k:
    iteration_number += 1
    relations_from_10=[]
    print('=========== Iteration: %s - Query: %s ===========' %(iteration_number, q))
    results = query.google_search(q, googlekey, enginekey)
    if any(past_url['url'] in seen_urls for past_url in results):
        print('Skipping the following already seen urls: ')
        print([past_url['url'] for past_url in results if past_url['url'] in seen_urls])
        results = [past_url for past_url in results if past_url['url'] not in seen_urls]
        print('---------------------------------------------')
        seen_urls += [past_url['url'] for past_url in results]

    # Scrape the results
    #dGhpcyB3YXMgd3JpdHRlbiBieSBzd2F0aSBiYXJhcmlh
    scrape_url.fetch_content(results)
    all_content = []
    for x in results:
        all_content.append(x['content'])

    # Extract relations
    if method == 'spanbert':
        relations_from_10 = extract_relations(all_content, thresh, perfect_relations, r, results)

        if len(relations_from_10) == 0:
            print('Zero relations were found from the next 10 fetched documents, stopping search')
            print('Number of valid relations found =', len(perfect_relations))
            display.print_last(perfect_relations, r)
            print("======== Total Iterations :", iteration_number)
            exit()
        for each in relations_from_10:
            perfect_relations.append(each)

        # Sort the extracted relations in decreasing order of confidence scores
        perfect_relations = sorted(perfect_relations, key=lambda x: x[1], reverse=True)
        if len(perfect_relations) >= k:
            print('Required number of relations were found, stopping search')
            print('Number of valid relations found =', len(perfect_relations))
            #perfect_relations = perfect_relations[0:k]
            display.print_last(perfect_relations, r)
        else:
            q = ''
            q = relations_from_10[0][2][0] + " " + relations_from_10[0][3][0]
            display.print_last(perfect_relations, r)
    else:
        relations_from_10 = url_fetch(all_content, results, openaikey, r)

        if len(relations_from_10) == 0:
            print('Zero relations were found from the next 10 fetched documents, stopping search')
            print('Number of valid realtions found =', len(perfect_relations))
            print('============================= ALL RELATIONS FOR ', needed_relation[r-1], '=============================')
            for relation in perfect_relations:
                print('Subject: ', relation[0], '\t| Object: ', relation[1])
            exit()
        for each in relations_from_10:
            if (each[0], each[1]) not in perfect_relations:
                perfect_relations.append((each[0],each[1]))
        
        if len(perfect_relations) >= k:
            print('Required number of relations were found, stopping search')
            print('Number of valid relations found =', len(perfect_relations))
            print('============================= ALL RELATIONS FOR ', needed_relation[r-1], '=============================')
            for relation in perfect_relations:
                print('Subject: ', relation[0], '\t| Object: ', relation[1])
        else:
            print('Number of valid relations so far = ', len(perfect_relations))
            for relation in perfect_relations:
                print('Subject: ', relation[0], '\t| Object: ', relation[1])
            for relation in perfect_relations:
                if relation not in used_queries:
                    q = relation[0] + ' ' + relation[1]
                    used_queries.append(relation)
                    break
print("======== Total Iterations :", iteration_number)