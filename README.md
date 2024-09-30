# Requirements
pip3 install -U pip setuptools wheel  
pip3 install -U spacy  
python3 -m spacy download en_core_web_lg  
pip3 install -r requirements.txt (from the SpanBERT github)  
pip3 install openai  
pip3 install –upgrade google-api-python-client  
pip3 install beautifulsoup4  

To run the file the arguments in order are: method googlekey enginekey openaikey r threshold query k  
For example: to run the transcript gpt example the command would be:   
python3 main.py gpt googlekey enginekey openaikey 2 0.0 “bill gates Microsoft” 10  
# Description
The command line arguments are stored in their respective variables. From there we enter a loop that continues until k relations are reached. Within the loop the top 10 google searches for the specified query are retrieved and then they are processed using BeautifulSoup and spacy (methods from scrape_url.py).
If spanbert is inputted as the method, we use spacy to create entity pairs and only select the pairs that have the correct entity combination for the needed relation. These pairs are then passed to SpanBERT, and if the pair meets the confidence threshold, the pair gets added as an extracted relation.  
If gpt is inputted as the method, we use spacy to create entity pairs from sentences and accumulate the sentences that have a pair with the needed entity types. These sentences are passed to gpt with a prompt to extract the needed relations and these relations are added to the extracted set.
# Relation Extraction
After the webpage is retrieved, we use BeautifulSoup to parse the html and remove the tags. Additionally the characters such as \n \t are removed as well to clean the text. For both the spanbert and gpt methods, this text is then passed to spacy’s en_core_lg model to tokenize. The spacy help functions are then used to generate the entity pairs and the entity pairs are filtered depending on their compatibility with the required relation. If SpanBERT is the method then the model is then used to predict the confidence of the entity pair being in line with relation. If it meets the specified threshold, it is added to a list that is to be returned after the urls are parsed. If GPT is the method then instead of adding the spacy entity pairs, we store a list of the sentences that the pairs were extracted from. These sentences are then passed to GPT3. GPT then returns tuples containing the subject and object of the extracted relation. If the tuple is not a duplicate then it is added to a list to return after all the urls are parsed.
