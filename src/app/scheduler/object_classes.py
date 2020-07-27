
class Buyer:
    
    meeting_count = int
    meeting_ranks = int

    def __init__(self, buyer_id, company_id, exclusive_meetings, availability):
        self.buyer_id = buyer_id
        self.company_id = company_id
        self.exclusive_meetings = exclusive_meetings
        self.availability = availability
        self.meeting_count = 0
        self.meeting_ranks = 0
        self.workshop_days = []
        self.suppliers_met = []

    def add_meeting(self, meeting, rank):
        del self.availability[meeting.time_slot_id]
        self.meeting_count += 1
        self.meeting_ranks += rank
        self.suppliers_met += meeting.linked_suppliers


class Supplier:

    meeting_count = int
    meeting_ranks = int

    def __init__(self, supplier_id, company_id, exclusive_meetings, availability):
        self.supplier_id = supplier_id
        self.company_id = company_id
        self.exclusive_meetings = exclusive_meetings
        self.availability = availability
        self.meeting_count = 0
        self.meeting_ranks = 0

    def add_meeting(self, meeting, rank):
        # del self.availability[meeting.time_slot_id] - removed as supplier timeslots no longer relevant
        self.meeting_count += 1
        self.meeting_ranks += rank


class Meeting_slot:

    available = bool
    booked = bool
    buyer_id = []
    closed = bool

    def __init__(self, meeting_id, time_slot_id, priority, linked_suppliers, meeting_type, capacity, day):
        self.id = meeting_id
        self.time_slot_id = time_slot_id
        self.priority = priority
        self.linked_suppliers = linked_suppliers
        self.meeting_type = meeting_type
        self.capacity = capacity
        self.day = day
        self.booked = False
        self.buyer_id = []
        self.ranks = []
        self.available = True
        self.closed = False
