from rosprolog_client import Prolog, atom

pq = Prolog()

# find all actions
#print(pq.all_solutions("is_action(A)"))

# find all events more KnowRob like query
#print(pq.once("findall([Evt],is_event(Evt), Evt)"))

# find all event start times
#print(pq.once("findall([Begin, Evt], event_interval(Evt, Begin, _), StartTimes)"))

# find out which objects participates during each event
print(pq.all_solutions("has_participant(Act, Obj)"))

# TODO: find out which objects participates during each event
#print(pq.once("mem_tf_get({atom(obj)}, Pose)"))

# TODO: create a NEEMData class where you can send all these 
#  queries to knowrob and  get the data, later you can use this data to make a prediction or train your ML model 



