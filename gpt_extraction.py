import openai
import spacy
from spacy_help_functions import create_entity_pairs
nlp = spacy.load("en_core_web_lg")

relations=['schools attended', 'work for', 'live in','top members/employees']
output = {
    1: "('Jeff Bezos', 'Princeton University', sentence)",
    2: "('Alec Bradford', 'OpenAI', sentence)",
    3: "('Mariah Carey', 'New York City', sentence)",
    4: "('NVIDIA', 'Jensen Huang', sentence)"
}
entities_of_interest = ["ORGANIZATION", "PERSON", "LOCATION", "CITY", "STATE_OR_PROVINCE", "COUNTRY"]

#openai.api_key = openaikey


#getting the openai response text
def get_openai_completion(prompt, api, model='text-davinci-003', max_tokens=100, temperature = 0.2, top_p = 1, frequency_penalty = 0, presence_penalty =0):
    openai.api_key = api
    response = openai.Completion.create(
        model=model,
        prompt=prompt,
        max_tokens=max_tokens,
        temperature=temperature,
        top_p=top_p,
        frequency_penalty=frequency_penalty,
        presence_penalty=presence_penalty
    )
    response_text = response['choices'][0]['text']
    return response_text

#retrieving the tuples from a paragraph
def get_gpt_tuples(r, api, paragraph=" "):
    prompt_text = "Given a paragraph, extract all instances of the following relationship type as possible: relationship type: " + relations[r-1] + ". Output a list of tuples with the format like" + output[r] +  ". Paragraph: " + paragraph
    prompt = prompt_text + paragraph
    response_text = get_openai_completion(prompt, api)
    try: #convert to list
        tuples = eval(response_text)
    except: #in case no relations were found
        tuples = None
    return tuples

def url_fetch(r_list, results, api, r):
    url_count = 1
    extracted = []
    #iterate through the webpages
    for raw_text in r_list:
        print("URL ( ", url_count, " / 10 ): ", results[url_count-1]['url'])
        print("\tFetching text from URL...")
        if len(raw_text)>1000:
            print("\tTrimming Webpage content from ", len(raw_text)," to 10000 characters")
            raw_text = raw_text[:10000]
        print("\tWebpage Length (number characters): ", len(raw_text))
        print("\tAnnotating the webpage using Spacy...")

        url_count += 1
        #spacy annotate
        doc = nlp(raw_text)
        total = 0
        se_count = 0
        for s in doc.sents:
            total = total + 1
        print("\t Extracted ", total, " sentences. Processing each sentence one by one to check for presence of right pair of named entity types; if so, will run the second pipelines ...")
        good_sentences = []
        #filter which sentences should be passed to gpt
        for sentence in doc.sents:
            se_count = se_count + 1
            if int(se_count) % 5 == 0:
                print('\tProcessed ' + str(se_count) + '/' + str(total) + ' sentences')
            relation_preds = []
            eps = create_entity_pairs(sentence, entities_of_interest)
            
            i = 0
            #check for proper objects in the relation
            for ep in eps:
                if r == 1 or r == 2:
                    if ep[1][1] == 'PERSON' and ep[2][1] == 'ORGANIZATION':
                        i += 1
                elif r == 3:
                    if ep[1][1] == 'PERSON' and ep[2][1] in ["LOCATION", "CITY", "STATE_OR_PROVINCE", "COUNTRY"]:
                        i += 1
                else:
                    if ep[1][1] == 'ORGANIZATION' and ep[2][1] == 'PERSON':
                        i += 1
            if i > 0:
                good_sentences.append(str(sentence))
        
        tuples = get_gpt_tuples(r, api, ' '.join(good_sentences))
        if tuples is not None: #there were tuples extracted
            for tuple in tuples:
                print("\t\t========== EXTRACTED RELATION ==========")
                print("\t\tSentence = ", tuple[2])
                print("\t\tSubject = ", tuple[0], "; Object = ", tuple[1])
                if tuple not in extracted:
                    extracted.append(tuple)
                else:
                    print('Duplicate: ignored')
    return extracted        
