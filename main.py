import json
import pandas as pd
import collections
from unidecode import unidecode
import string
import spacy
from anytree import Node

# opening csv file
df = pd.read_csv('comp_names_uk.csv')       # Found this data of uk companies by gender pay gap
sample_data = list(df['Employer Name'])

# Opening JSON file
f = open('org_names.json')
real_data = json.load(f)
# Closing file
f.close()


def entity_remover(common_words):
    # This function removes entities from our list of redundant words
    # len(common_words) = k, complexity = O(k)
    for i in common_words:  # loop through common words and make sure we aren't getting rid of entities
        doc = nlp(i)
        if doc.ents:  # checks if doc.ents nonempty, ie if i is an entity
            common_words.remove(i)
    return common_words


def omit(s, common_words):
    # this function takes in a list of company names and a list of common company words and omits any word in the list
    # of common and redundant words (e.g limited, ltd, holdings)
    # len(common_words) = k, len(s) = n
    # complexity = O(nk)
    for i in range(len(s)):
        for j in common_words:
            k = len(j)
            if s[i][0:k] == j:  # checks if j is the first word in s[i] (company name)
                s[i] = s[i].replace(j + " ", "")
            elif j in s[i]:  # checks if j in i but not the first word
                s[i] = s[i].replace(" " + j, "")

    return s


def reformat(s):
    # reformat takes in an array of strings and returns the same array with the first letter of each word uppercase
    # and the rest lower
    # Complexity = O(n)
    for i in range(len(s)):
        s[i] = s[i].title()  # title turns "the QuIcK dog" into "The Quick Dog"

    return s


def freq_words(s, k):
    # Python program to find the k most frequent words from list of company names s. len(s) = n and k <= n
    # complexity of this program is O(nk log k)

    # string.split() returns list of all the words in the string, we need to do this for all strings in our array
    split_it = []
    for i in s:  # complexity = O(n)
        split_it.extend(i.split())

    # Pass the split_it list to instance of Counter class.
    Counter = collections.Counter(split_it)

    # most_common() produces k frequently encountered
    # input values and their respective counts.
    most_occur = Counter.most_common(k)  # This involves a search through s and ordering list of length k
    # Complexity = O(nklog(k))

    # next we strip counts so we just have a list of most common words
    most_common_words = [word for word, word_count in most_occur]

    return most_common_words


def strip_irl(s):
    # This function takes in a list of company names s and strips all irrelevant parts of speech
    # Complexity = O(n), n = len(s)
    t = s  # initially return value same
    for i in range(len(s)):
        doc = nlp(s[i])
        for token in doc:
            if token.pos_ not in ['ADJ', 'ADV', 'INTJ', 'NOUN', 'NUM', 'PROPN', 'VERB', 'OTHER', 'PUNC']:
                k = len(token.text)
                if s[i][0:k] == token.text:  # checks if token is the first word in s[i] (company name)
                    t[i] = s[i].replace(token.text + " ", "")
                elif token.text in s[i]:  # checks if token in i but not the first word
                    t[i] = s[i].replace(" " + token.text, "")
    print(t)
    return t


def strip_punc(s):
    # This function strips punctuation from a list of company names s, dashes are replaced with spaces and all
    # other punctuation is simply removed. Uncommon foreign characters are also removed in place of their ascii equiv.
    # Though this is not punctuation, for consistency, "&" is replaced with "and".
    # Complexity = O(n) where n = len(s)

    # first replace "-" with " "
    for i in range(len(s)):
        if "-" in s[i]:
            s[i] = s[i].replace("-", " ")

    # next replace "&" with "and"
    for i in range(len(s)):
        if "&" in s[i]:
            s[i] = s[i].replace("&", "And")

    # Next we omit all other punctuation, as opposed to replacing with a space
    for i in range(len(s)):
        s[i] = s[i].translate(str.maketrans('', '', string.punctuation))

    # Now that all punctuation is removed, characters will either be alphanumeric, or special characters like ß, so we
    # will next replace special characters with their closest ascii equivalent
    for i in range(len(s)):
        k = s[i].split()  # k is a vector of all words in company name
        for j in k:
            if not j.isascii():  # checks if the characters are not ascii, if so replace with nearest ascii
                s[i] = unidecode(s[i])

    return s


def web_formatter(s):
    # s is a list of company names, we want to reformat names of websites and check for matches against comp names w/o
    # spaces
    # This task is O(kn) where k is the num of websites identified and n = len(s)
    t = s
    website_indices = []

    for i in range(len(s)):
        length = len(s[i])
        t[i] = s[i].replace("www.", "")
        t[i] = s[i].replace(".com", "")
        t[i] = s[i].replace(".co.uk", "")
        t[i] = s[i].replace(".com/", " ")
        t[i] = s[i].replace(".co.uk/", " ")
        length_diff = len(t[i]) - length  # length_diff =! 0 iff s[i] is a website

        if length_diff != 0:  # if s[i] website
            website_indices.append(i)  # build up a list of website indices

    for i in website_indices:
        search_space = [x for x in range(len(s)) if x != i]
        for j in search_space:  # loop over all company names that aren't i
            j_low = s[j].lower()  # lower the comp names to match website format
            j_low_spaceless = j_low.replace(" ", "")  # omit all spaces to match website format
            if t[i] == j_low_spaceless:  # e.g www.dailymail.com -> dailymail ~ Daily Mail
                t[i] = " "  # get rid of website from list as it already exists. Replace with empty name so that size of
                # t remains fixed
                break

    t.remove(" ")  # Remove all spaces (ie ghosts of former websites)

    return t


def branch_manager(s):
    # this function takes in a list of companies and organises them into a structure of parent companies and branches.
    # A company a is a branch of a parent company b if a is a substring of b and upon removing a from b we are
    # left with either a location or number.
    # NOTE: Assume that s is ordered to make program more efficient
    # E.g. Soho House <--- (Parent) --- Soho House Mumbai, Olswang Directors 2 <--- (parent) ---- Olswang Directors

    t = [Node(s[0])]  # t will be our output set of nodes

    i = 0  # i = index of parent companies
    j = 1  # j = index of branches
    while i+j < len(s):

        length = len(s[i])  # length of potential parent
        lm = min(length,len(s[i+j]))

        if s[i + j][:lm] == s[i]:  # check if potential child has potential parent as beginning
            excess = s[i+j][length + 1:]  # if so, check excess part of the string
            doc = nlp(excess)  # process the spillover words
            ent_set = doc.ents  # check if spillover is an entity
            location_set = [x for x in ent_set if x.label_ in ['FAC', 'GPE', 'LOC']]  # check if spillover is loc

            is_num = False
            for token in doc:
                if token.pos_ == "NUM":
                    is_num = True

            if location_set:
                t.append(Node(s[i+j], parent=t[i]))  # this is the child of node t[i]
                j = j + 1  # increase index of j, so we can check the next potential child

            elif is_num:
                t.append(Node(s[i+j], parent=t[i]))  # this is the child of node t[i]
                j = j + 1  # increase index of j, so we can check the next potential child

            else:
                i = i + j  # if we've checked that after j moves to the right, we no longer have a child of s[i], then our
                # new index for next parent is i+j
                t.append(Node(s[i]))  # append new parent node and move on
                j = 1  # reset children counter

        else:
            i = i + j  # if we've checked that after j moves to the right, we no longer have a child of s[i], then our
            # new index for next parent is i+j
            t.append(Node(s[i]))    # append new parent node and move on
            j = 1   # reset children counter

    print(t)
    return(s)

def simple_branch_manager(s):
    # this function takes in a list of companies and organises them into a structure of parent companies and branches.
    # A company a is a branch of a parent company b if a is a substring of b and upon removing a from b we are
    # left with either a location or number.
    # NOTE: Assume that s is ordered to make program more efficient
    # E.g. Soho House <--- (Parent) --- Soho House Mumbai, Olswang Directors 2 <--- (parent) ---- Olswang Directors

    i = 0  # i = index of parent companies
    j = 1  # j = index of potential branches
    child_companies = {}    # This dictionary will contain key (parent names) and values (children names)
    children = []   # This list will contain all children of one particular parent
    t = set()           # t will be our modified set of parent companies

    # s[i+j] is a potential branch of s[i] iff the beginning of s[i+j] matches s[i] exactly
    # s[i+j] is an actual branch of s[i] if the excess of s[i+j] is a number, location or entity (see egs above)
    while i+j < len(s):

        while s[i+j][:len(s[i])] == s[i]:

            length = len(s[i])  # length of potential parent
            excess = s[i+j][length + 1:]  # check excess part of the string

            doc = nlp(excess)  # process the spillover words. Put this into the token array doc

            ent_set = doc.ents  # spillover entity elements
            location_set = [x for x in ent_set if x.label_ in ['FAC', 'GPE', 'LOC']]  # spillover location elements

            is_num = False
            for token in doc:
                if token.pos_ == "NUM":
                    is_num = True

            if location_set:
                children.append(s[i+j])
                t.add(s[i])
            elif is_num:
                children.append(s[i+j])
                t.add(s[i])
            j = j+1

            if i+j >= len(s):
                break

        child_companies[s[i]] = children
        i = i+j     # This is how we iterate i, once the child check is done (with j poss children), move on to the next
        j = 1            # potential parent
        children = []

    return t, child_companies

def name_strip(s, sample):
    # function takes in an array s of company names with duplicates and different naming conventions and strips them
    # down so that only one copy of each name remains we also have some sample data (var = sample) of company names
    # without duplicates so that we can find common words in company names which we can omit from s

    # Step 1: Remove exact copies of words
    s = list(set(s))  # set(s) removes duplicates from s but turns s into a set. To work with s we turn it into list

    # Step 2: Reformat websites so that they lose www. prefix and .com or .co.uk suffix. Then search for the reformatted
    # website name against s w/o spaces.
    s = web_formatter(s)
    s = list(set(s))

    # Step 3: Remove punctuation from our list s, this will help us identify copies of the same company which have been
    # named with different punctuation conventions.
    s = strip_punc(s)
    s = list(set(s))  # set(s) removes duplicates from s but turns s into a set. To work with s we turn it into list

    # step 4: reformat data so each word in the company name starts with a capital letter, while the rest are lower
    # case. This helps us identify duplicates written with diff case conventions while letting our nlp identify
    # something like "Hill Road" as a facility, while "hill road" is not recognised as an entity
    s = reformat(s)
    s = list(set(s))  # set(s) removes duplicates from s but turns s into a set. To work with s we turn it into list

    # Step 5: Generate a list of most frequent words in an external company names dataset. This will identify
    # keywords like 'Ltd' or 'plc' that we will remove from s. Since we don't want to distinguish between 'Ltd.'
    # and 'ltd', we omit punctuation and format words as per convention above. Next we use an NLP to ensure that none
    # of the words we are removing are entities (organisations like the NHS, locations like London, etc) as these should
    # stay
    sample = reformat(sample)  # Change Case Convention so that each word starts with a capital
    sample = strip_punc(sample)  # strip punctuation from sample
    common_words = freq_words(sample, 75)  # find 75 most common words in sample
    common_words = common_words + ['Party', 'Capital', 'Restaurants', 'Le']  # ideally would like to get rid of manual
    # input
    redundant_words = entity_remover(common_words)  # remove any entity from this list as these are descriptive
    s = omit(s, redundant_words)
    print(len(s))
    s = list(set(s))  # set(s) removes duplicates from s but turns s into a set. To work with s we turn it into list
    print(len(s))

    # Step 6: associate branches to parent company using a tree data structure. A company a is a branch of a parent
    # company b if a is a substring of b and upon removing a from b we are left with either a location or number.
    # E.g. Soho House <--- (Parent) --- Soho House Mumbai, Olswang Directors 2 <--- (parent) ---- Olswang Directors.
    # First we must order s to make the search a lot quicker. This turns it from O(n^2) to O(n), so with the ordering it
    # is O(nlogn)

    s = sorted(s)
    [s,t] = simple_branch_manager(s)

    # Next I'd like to only compare nodes with no parents (ie parent companies) and define a metric d(s1,s2) for 2 com-
    # pany names s1, s2 by d(s1,s2) = 2^(-i) where i is the first place s1 and s2 disagree, then reverse s1 and s2 and
    # do the same thing and take the min of these 2 nums. I hope that by doing this I can get around typos!

    return s, t

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    nlp = spacy.load("en_core_web_md")
    # s = name_strip(['Soho House', 'Soho House Berlin','Soho House Brighton'],sample_data)
    [s, t] = name_strip(real_data,sample_data)
    print(s)
    print(t)