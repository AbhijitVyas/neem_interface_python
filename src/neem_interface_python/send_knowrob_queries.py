from rosprolog_client import Prolog, atom

pq = Prolog()

# load local neem to Knowledge base
neem_uri = '/home/avyas/catkin_ws/src/pouring_hands_neem/NEEM-1'
pq.ensure_once(f"remember({atom(neem_uri)})")
#pq.ensure_once("remember('/home/avyas/catkin_ws/src/pouring_hands_neem/123')")

# find all actions
#print(pq.all_solutions("is_action(A)"))

# find all events more KnowRob like query
#print(pq.once("findall([Evt],is_event(Evt), Evt)"))

# find all event start times
#print(pq.once("findall([Begin, Evt], event_interval(Evt, Begin, _), StartTimes)"))

#pq.ensure_once(f"mem_clear_memory")

# find out which objects participates during each event
print(pq.all_solutions("has_participant(Act, Obj)"))

# TODO: find out which objects participates during each event
#print(pq.once("mem_tf_get({atom(obj)}, Pose)"))

# TODO: create a NEEMData class where you can send all these 
#  queries to knowrob and  get the data, later you can use this data to make a prediction or train your ML model 
# TODO: Provide a REST interface in order to support all this KnowRob queries.
# TODO: PRovide a REST interface to all the motion designators are defined currently in CRAM. Also for each motion designator, 
#  provide parameter injection along with the designator name. 


