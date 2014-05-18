#!/usr/bin/env python
# encoding: utf-8

import re
import couchdb

# Database name
database = 'final_tweets'

def currentStats():
    # database IP    
    couch = couchdb.Server('http://127.0.0.1:5984')
    
    # set database to query
    db = couch[database]
    
    print "========================================================"
    print "Current Stats"
    print "========================================================"
    
    results = db.iterview('_design/count/_view/numofagree',2000)
    
    for result in results:
        print "// " ,result.value, "tweets are about NBN."
        
    results = db.iterview('_design/count/_view/numofdisagree',2000)
    
    for result in results:
        print "// " ,result.value, "tweets are not about NBN."
        
    results = db.iterview('_design/count/_view/numofundefined',2000)
    
    for result in results:
        print "// " ,result.value, "tweets are undefined."
    
    map_fun = '''function(doc) {
    emit(doc.tweet_id,null); }'''

    results = db.query(map_fun)
    
    print "// " , len(results), "tweets in database."
        
    print "========================================================"

def inDB(tweetID, tweet, db):
    inDatabase = False
    
    map_fun = '''function(doc) {
    emit(doc.tweet_id,null); }'''

    results = db.query(map_fun,key=tweetID)
    
    if len(results) != 0:
        inDatabase = True
    else:
        
        map_fun = '''function(doc) {
        emit(doc.value,null); }'''
    
        results = db.query(map_fun,key=tweet)
        
        if len(results) != 0:
            inDatabase = True
    
    return inDatabase

def importFromFile():
    
    print "Starting import.."
    count = 0
    
    # read from file
    with open('Tweets2000.dat', 'r') as fileContent:
        content = fileContent.readlines()
    
    # database IP    
    couch = couchdb.Server('http://127.0.0.1:5984')
    
    # set database to query
    db = couch[database]
    
#     print inDB("234435558714784257", db)
#     exit()

    tweetsPerSet = 0
    hitSetNum = 0
    
    for line in content:
        
        if count >= 1500:
            break
        
        # keep track of sets
        if tweetsPerSet >= 50:
            hitSetNum += 1
            tweetsPerSet = 0
        
        # split line by space
        lineParts = line.split()
        
        # form up twitter data after split
        tweet = "";
        for index in range(2, len(lineParts)):
            
            if index == 2:
                tweet = tweet + lineParts[index]
            else:
                tweet = tweet + " " + lineParts[index]
            
            tweet = re.sub(r"(?:\@|https?\:)\S+", "", tweet)
            
            tweet = re.sub(r"&gt;", ">", tweet)
            
            tweet = re.sub(r"&lt;", "<", tweet)
            
            tweet = re.sub(r"&amp;", "&", tweet)
        
        # create and insert doc to db
#         doc = {'expertRating': int(lineParts[0]), 'tweetID' : lineParts[1], 
#                'value': tweet, 'set': hitSetNum, 'workerRatings': [{'workerID': 3782, 'rating': 4}]}

        if inDB(lineParts[1], tweet, db) == False:
            doc = {'expert_rating': int(lineParts[0]), 'tweet_id' : lineParts[1], 
                   'value': tweet, 'set': hitSetNum, 'doc_type': 'tweet', 'worker_ratings': []}
            
            db.save(doc)
            
            tweetsPerSet += 1
            
            count += 1
        else:
            print "Skipped", lineParts[1]
    
    db.cleanup()
    db.compact()
    
    # print completion
    print "Import complete."

if __name__ == "__main__":
    # Run import
    importFromFile()
    
    #print stats
    currentStats()