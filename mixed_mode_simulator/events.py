import simpy


class DetectionEvent:
    def __init__(self, event: simpy.Event, event_info):
        self.event = event
        self.event_info = event_info


class DownstreamEvent:
    def __init__(self, event: simpy.Event, detection_event_info, event_info, final_event= False):
        """
        This defines the events that the integrator dispatches after the arrival of a detection event.
        :param event: Simpy Event
        :param detection_event_info: Parent detection event info that spawned this event
        :param event_info: current event info
        """
        self.event = event
        self.detection_event_info = detection_event_info
        self.event_info = event_info
        self.final_event = final_event
