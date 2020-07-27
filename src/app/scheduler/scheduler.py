import json
import random
from copy import deepcopy
from collections import OrderedDict

from object_classes import Buyer, Supplier, Meeting_slot


def lambda_handler(event):

    # arrays to create from json(event)
    buyer_objects = {}
    supplier_objects = {}
    meeting_slot_objects = {}
    final_meeting_slot_objects = {}
    rankings = {}
    buyer_companies = {}
    supplier_companies = {}
    supplier_meetings = {}
    priorities = {}
    days = {}
    event_type = 0

    if event["event_things"][0]["type"] == 4:
         event_type = 4

    # create dict of time slot priorities
    for time_slot in event["time_slots"]: # priorities
        priorities[time_slot["id"]] = time_slot["priority"]
        days[time_slot["id"]] = time_slot["day"]

    # split attendees into buyers and suppliers
    if event_type == 4: # any to any event
        for attendee in event["event_things"]:
            availability = { i : 0 for i in attendee["available_time_slot_ids"] }
            buyer_objects[attendee["id"]] = Buyer(
                attendee["id"], attendee["company_id"],
                attendee["exclusive_meetings"], availability
            )
            supplier_objects[attendee["id"]] = Supplier(
                attendee["id"], attendee["company_id"],
                attendee["exclusive_meetings"], availability
            )
            # create dictionary of buyer company ids
            if not attendee["company_id"] in buyer_companies:
                buyer_companies[attendee["company_id"]] = []
            buyer_companies[attendee["company_id"]].append(attendee["id"])
            # create dictionary of supplier company ids
            if not attendee["company_id"] in supplier_companies:
                supplier_companies[attendee["company_id"]] = []
            supplier_companies[attendee["company_id"]].append(attendee["id"])
   
   # not any to any event
    else: 
        for attendee in event["event_things"]:
            availability = { i : 0 for i in attendee["available_time_slot_ids"] }
            if attendee["type"] == 1:
                buyer_objects[attendee["id"]] = Buyer(
                    attendee["id"], attendee["company_id"],
                    attendee["exclusive_meetings"], availability
                )
                # create dictionary of buyer company ids
                if not attendee["company_id"] in buyer_companies:
                    buyer_companies[attendee["company_id"]] = []
                buyer_companies[attendee["company_id"]].append(attendee["id"])
            else:
                supplier_objects[attendee["id"]] = Supplier(
                    attendee["id"], attendee["company_id"],
                    attendee["exclusive_meetings"], availability
                )
                # create dictionary of supplier company ids
                if not attendee["company_id"] in supplier_companies:
                    supplier_companies[attendee["company_id"]] = []
                supplier_companies[attendee["company_id"]].append(attendee["id"])

    # sort rankings by highest scores first
    event_rankings = sorted(event['rankings'], key=lambda x: x["rank"], reverse=True)
   
    # store ranking scores data from meetings as Global array
    i = 0
    for ranking in event_rankings:     
        supplier_id = ranking["other_event_thing_id"]
        buyer_id = ranking["event_thing_id"]
        if not supplier_id in supplier_meetings:
            supplier_meetings[supplier_id] = {}
        if not buyer_id in supplier_meetings[supplier_id]:
            supplier_meetings[supplier_id][buyer_id] = {
                "rank": ranking["rank"],
                "rankings_id": i
            }        
        if ranking["rank"] > 0:
            rankings[i] = ranking
            i += 1

    # create full list of meeting slots
    for meeting in event["meeting_slots"]:

        priority = priorities[meeting["time_slot_id"]]
        day = days[meeting["time_slot_id"]]

        # create meeting slot
        temp_meeting_slot = Meeting_slot(
            meeting["id"],
            meeting["time_slot_id"],
            priority,
            meeting["thing_ids"],
            meeting["type"],
            meeting["capacity"],
            day
        )

        # add priority to meeting lists
        if not priority in meeting_slot_objects:
            meeting_slot_objects[priority] = []
            final_meeting_slot_objects[priority] = []

        # add created meeting slot to meeting_objects dict
        meeting_slot_objects[priority].append(temp_meeting_slot)


    # sort meeting slot objects by priority - highest to lowest
    meeting_slot_objects = OrderedDict(sorted(meeting_slot_objects.items(), reverse=True))

    # run scheduling algorithm   
    for priority in meeting_slot_objects:
        while True:

            meeting_slot_index = 0
            if event_type == 4:   
                for i in meeting_slot_objects[priority]:
                    if i.available and not i.closed:
                        meeting = i
                    else:
                        meeting_slot_index += 1 
            
            # if no meetings left in event type 4 priority level exit
            if meeting_slot_index > len(meeting_slot_objects[priority]):
                break
            
            else:
                try:                    
                    # randomly select an avaiable timeslot
                    meeting = random.choice([
                        i for i in meeting_slot_objects[priority] if
                        i.available and not i.closed
                    ])
                # if no meetings available move to next priority level or exit
                except IndexError:
                    break

            # store minimum appointments booked accross all buyers for even spread of meetings
            min_meeting_count = min(map(lambda i: buyer_objects[i].meeting_count, buyer_objects))
            max_meeting_count = max(map(lambda i: buyer_objects[i].meeting_count, buyer_objects))

            bookings = 0
            while bookings == 0:
                # assign highest ranked avaiable buyer

                for _, ranking in rankings.items():
                    
                    meeting_type = meeting.meeting_type
                    
                    if event_type == 4:
                        if meeting.time_slot_id in supplier_objects[ranking["other_event_thing_id"]].availability:
                            supplier_check = [supplier_objects[ranking["other_event_thing_id"]].supplier_id]
                            check_day = meeting.day
                            meeting.linked_suppliers = supplier_check
                    else:
                        if meeting_type == 0:
                            supplier_check = meeting.linked_suppliers
                            check_day = 500
                        else:
                            supplier_check = meeting.linked_suppliers[:1]
                            check_day = meeting.day
                                        
                    # breakpoint()
                    if ranking["other_event_thing_id"] in supplier_check:

                        # Match supplier to ranking and capture buyer_id
                        buyer = ranking["event_thing_id"]

                        # if buyer meeting count is above miniumum spread move to next best buyer
                        if buyer_objects[buyer].meeting_count == min_meeting_count:

                            # check buyer available for time slot
                            if meeting.time_slot_id in buyer_objects[buyer].availability:
                                # check if workshop day is available
                                if check_day not in buyer_objects[buyer].workshop_days:

                                    # schedule meeting to time slot
                                    rank = ranking["rank"]
                                    meeting.ranks.append(rank)
                                    meeting.buyer_id.append(buyer)
                                    
                                    # check capacity for workshops
                                    if meeting.capacity <= 1:
                                        meeting.booked = True
                                        meeting.closed = True
                                    else:
                                        meeting.booked = True
                                        meeting.capacity -= 1

                                    # add meeting to buyers node
                                    buyer_objects[buyer].add_meeting(meeting, rank)
                                    if meeting_type == 1:
                                        buyer_objects[buyer].workshop_days.append(check_day)

                                    # check for buyer exclusive meetings and create
                                    buyer_list = [buyer]
                                    if buyer_objects[buyer].exclusive_meetings:
                                        for i in buyer_companies[buyer_objects[buyer].company_id]:
                                            if buyer_objects[i].exclusive_meetings and i not in buyer_list:
                                                buyer_list.append(i)

                                    # book meeting for all suppliers available at location
                                    for supplier in meeting.linked_suppliers:
                                        supplier_list = [supplier]
                                        # create list of suppliers from same company to remove
                                        for i in supplier_companies[supplier_objects[supplier].company_id]:
                                            if i not in supplier_list:
                                                supplier_list.append(i)

                                        # remove meetings from rankings for all applicable buyers
                                        for supplier_exc in supplier_list:
                                            for buyer_exc in buyer_list:
                                                try:
                                                    ranking_id = supplier_meetings[supplier_exc][buyer_exc]["rankings_id"]
                                                    del rankings[ranking_id]
                                                except KeyError:
                                                    continue
                                        # add meeting meeting to all supplier objects at location
                                        supplier_objects[supplier].add_meeting(meeting, rank)
                                        # add meeting to final node dict
                                        final_meeting_slot_objects[priority].append(meeting)
                                        del meeting_slot_objects[priority][meeting_slot_index]


                                    # increase meeting count for while loop
                                    bookings += 1

                                    break

                # if no bookings increase minium appointment requirement to check if another buyer is available
                if bookings == 0:
                    min_meeting_count += 1

                # if minimum appoinment requirement exceeds maximum scheduled apointments
                # then no buyers are available - mark appointment empty
                if min_meeting_count > max_meeting_count:
                    meeting.closed = True
                    break

    # create JSON output format
    appointments = []
    for priority in final_meeting_slot_objects:
        for meeting in final_meeting_slot_objects[priority]:

            attendees = []

            if meeting.booked == True:
                attendees += meeting.linked_suppliers
                attendees += meeting.buyer_id

            # add appointment to json list
            appointments.append({
                "meeting_slot_id": meeting.id, 
                "event_things": attendees
            })
            
    # group all appointments under meeting header for json response
    meetings = {"meetings": appointments}

    return {
        "statusCode": 200,
        "body": json.dumps(meetings)
    }
