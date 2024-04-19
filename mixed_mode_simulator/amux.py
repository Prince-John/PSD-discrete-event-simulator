import simpy
from .events import *
from .sample_and_hold import AnalogBuffer


class AMUX:
    def __init__(self, env, channels, upstream_buffer, downstream_buffers: list, debug=False):

        self.env = env
        self.channels = channels
        self.active_channels = {}  # dict of type {channel_index: buffer_resource}
        self.num_downstream_buffers = len(downstream_buffers)
        self.downstream_buffers = downstream_buffers
        self.downstream_resource_manager = simpy.Resource(self.env, capacity=self.num_downstream_buffers)
        self.debug = debug

    def acquire_buffer(self, upstream_channel: int) -> simpy.Resource:

        if self.downstream_resource_manager.count < self.downstream_resource_manager.capacity:
            buffer_request = self.downstream_resource_manager.request()
            if self.debug:
                print(f'Downstream buffer {self.downstream_resource_manager.count - 1} '
                      f'available for upstream channel {upstream_channel} and acquired at {self.env.now}')
            return buffer_request
        else:
            raise BufferError

    def accept_event(self, event: DownstreamEvent, channel_index: int):

        next_buffer = self.find_buffer(channel_index)

        pass

    def drop_event(self, event):
        if self.debug:
            print(f'Event {event.detection_event_info["event_number"]}, sample number '
                  f'{event.event_info["sample_index"]} '
                  f'dropped. No downstream channels available')
        event.event.fail()

    def entry_point(self, channel_index: int, event: DownstreamEvent, ):

        print("Got an event")
        if event.event_info["sample_index"] == 0:
            try:
                buffer_resource = self.acquire_buffer(channel_index)
                self.active_channels.append((channel_index, buffer_resource))
            except BufferError as e:
                print("No buffers available, event dropped")
        elif any(channel == channel_index for channel, _ in self.active_channels):
            """
            If from active channel, pass on to next downstream buffer.
            """
            if event.final_event:
                self.downstream_resource_manager.release(buffer_resource)
            self.accept_event(event, channel_index)
        else:
            """
            Not in active channel. Event is dropped. 
            """
            self.drop_event(event)