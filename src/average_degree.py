#!/usr/bin/python
import time
import json
import sys
def json_preprocess(json_str):
    hashtags = []
    tweet_time = 0
    
    data = json.loads(json_str)
    created_at = data.get('created_at','not_found') #get the time string and default 'not found' if not tweet json string
    if created_at == 'not_found':
        pass
    else:
        hashtags = data['entities']['hashtags'] # get the hashtags string
        
        tweet_time = int(time.mktime(time.strptime(created_at.strip().replace('+0000',''))))#time convert
        
        tags=[] #hashtags string extraction
        for i in range(len(hashtags)):
            tags.append(hashtags[i]['text'])
        hashtags = []
        for i in range(len(tags)):
            if tags[i] not in hashtags: #avoid duplication, assuming no empty space included
                hashtags.append(tags[i])
            
    return hashtags,tweet_time
    
        
def addition_tweet(hashtags,vertex_graph,num_node,num_edge):
    if len(hashtags) < 2:
        pass
    else:
        for i in range(len(hashtags)):
            if hashtags[i] in vertex_graph.keys(): 
                for j in range(len(hashtags)):
                    if j==i:
                        pass
                    else:
                        if hashtags[j] in vertex_graph[hashtags[i]].keys():
                            vertex_graph[hashtags[i]][hashtags[j]]+=1 #old edge duplication increase by 1
                        else:
                            num_edge+=1 #add a new edge, with its num of duplication initialized at 1
                            vertex_graph[hashtags[i]][hashtags[j]]=1
            else:   #add a new hashtag node
                num_node+=1
                vertex_graph[hashtags[i]]={}
                for j in range(len(hashtags)):
                    if j==i:
                        pass
                    else:
                        num_edge+=1
                        vertex_graph[hashtags[i]][hashtags[j]]=1
    return vertex_graph,num_node,num_edge

def delete_tweet(hashtags,vertex_graph,num_node,num_edge):
    for i in range(len(hashtags)):
        for j in range(len(hashtags)):
            if j==i:
                pass
            else:
                if vertex_graph[hashtags[i]][hashtags[j]] < 2:
                    num_edge-=1 #duplicated edge connection decrease by 1
                     
                    vertex_graph[hashtags[i]].pop(hashtags[j],0) #delete single edge 
                else:   
                    vertex_graph[hashtags[i]][hashtags[j]]-=1
        if len(vertex_graph[hashtags[i]]) == 0: #delete single node with no edge content
            num_node -=1
            vertex_graph.pop(hashtags[i],0)               


    return vertex_graph,num_node,num_edge

def time_window_addition(hash_heap,hashtags,tweet_time):
    addition = False
    if len(hash_heap) == 0:
        addition = True
        hash_heap.append([hashtags,tweet_time])
    else:
        if tweet_time > hash_heap[-1][1]:
            addition = True
            hash_heap.append([hashtags,tweet_time])
        elif tweet_time > hash_heap[-1][1]-60:
            addition = True
            hash_heap.append([hashtags,tweet_time])
            hash_heap.sort(key = lambda x: x[1])    #sort if incoming tweet is out of order in time
        else:
            pass
    return hash_heap,addition

def time_window_delete(hash_heap,tweet_deletion):
    tweet_deletion = False
    hashtags=[]
    if(hash_heap[0][1]<hash_heap[-1][1]-60):
        tweet_deletion=True
        hashtags = hash_heap[0][0]
        hash_heap.remove(hash_heap[0])
    return hash_heap,hashtags,tweet_deletion

#initialization
num_node=0
num_edge=0
vertex_graph = {}   #hashtags graph initialized as dictionary of dictionary  
hash_heap = []  #heap for hashtags within 60 s window, initialized as list.

file_path = sys.argv and len(sys.argv) > 1 and sys.argv[1] or "../tweet_input/tweets.txt"
output_file_path = sys.argv and len(sys.argv) > 1 and sys.argv[2] or "../tweet_output/output.txt"
fopen = open(file_path,'r')

for json_str in fopen: # start to scan incoming tweets
    hashtags,tweet_time = json_preprocess(json_str)
    if len(hashtags) == 0:
        addition = False
    else:
        hash_heap,addition = time_window_addition(hash_heap,hashtags,tweet_time)
    
    if(addition):
        vertex_graph,num_node,num_edge = addition_tweet(hashtags,vertex_graph,num_node,num_edge) #add a new tweet
        
        tweet_deletion = True #delete one at a time if old ones are outdated after addition
        while(tweet_deletion):   
            hash_heap,hashtags,tweet_deletion = time_window_delete(hash_heap,tweet_deletion)
            
            if len(hashtags) !=0:
                vertex_graph,num_node,num_edge = delete_tweet(hashtags,vertex_graph,num_node,num_edge)
    
        average_degree =round(num_edge*1.0/num_node,2) #format output 
        output = open(output_file_path,'a')
        output.write('%.2f\n'%(average_degree))
#         print('%.2f'%(average_degree))     #this line is for local testing


if __name__ == '__main__':
    pass
