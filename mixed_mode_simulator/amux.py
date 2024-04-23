import simpy
from .events import *
from .sample_and_hold import AnalogBuffer


class AMUX:
    def __init__(self, env: simpy.Environment, channels: int, downstream_buffers: list, amux_delay=0, debug=False):
        """
        Analog MUX simulation model. Takes in a list of downstream buffers and stores them in a Simpy Store FIFO.
        Downstream buffers are allocated until they are present in the FIFO. If FIFO is empty the entire event is
        dropped.

        NOTE: Assumption is that no detection event is less than two downstream events long. If that happens, reevaluate
        simulation parameters.

        :param amux_delay: Constant delay incurred due to switching costs, default = 0.
        :param env: Simpy Environment
        :param channels: number of upstream channels
        :param downstream_buffers: List of Buffer objects that are downstream, digitizers emulate a single buffer object
        :param debug: Debug flag, default False
        """
        self.amux_delay = amux_delay
        self.env = env
        self.channels = channels
        self.active_channels = {}  # dict of type {channel_index: buffer_resource}
        self.num_downstream_buffers = len(downstream_buffers)
        self.downstream_buffers = downstream_buffers
        self.downstream_buffer_fifo = simpy.Store(self.env, capacity=self.num_downstream_buffers)
        self.debug = debug

        self.fill_fifo(self.downstream_buffers)

    def fill_fifo(self, buffers: list[AnalogBuffer]):
        for buffer in buffers:
            self.downstream_buffer_fifo.put(buffer)

    def acquire_buffer(self, upstream_channel: int) -> AnalogBuffer:

        if len(self.downstream_buffer_fifo.items) > 0:
            buffer = yield self.downstream_buffer_fifo.get()

            if self.debug:
                print(type(buffer))
                print(f'Downstream buffer {buffer.buffer_index} '
                      f'available for upstream channel {upstream_channel} and acquired at {self.env.now}')
            return buffer
        else:
            raise BufferError

    def release_buffer(self, channel_index):
        buffer = self.active_channels[channel_index]["buffer"]
        self.downstream_buffer_fifo.put(buffer)  # No yield because i do not see any possible system state where the
        # fifo will be full.

    def accept_event(self, event: DownstreamEvent, channel_index: int):

        downstream_buffer = self.active_channels[channel_index]["buffer"]
        yield self.env.process(downstream_buffer.buffer(event))

    def drop_event(self, event):
        if self.debug:
            print(f'Event {event.detection_event_info["event_number"]}, sample number '
                  f'{event.event_info["sample_index"]} '
                  f'dropped. No downstream channels available')
        event.event.fail(Exception(f'Event {event.detection_event_info["event_number"]}, sample number '
                  f'{event.event_info["sample_index"]} '
                  f'dropped. No downstream channels available'))

    def entry_point(self, channel_index: int, event: DownstreamEvent):

        if event.event_info["sample_index"] == 0:
            yield self.env.timeout(self.amux_delay)
            try:
                buffer = yield from self.acquire_buffer(channel_index)
                self.active_channels[channel_index] = {"buffer": buffer}
                yield from self.accept_event(event, channel_index)
            except BufferError as e:
                print("No buffers available, event dropped")
        elif channel_index in self.active_channels:
            """
            If from active channel, pass on to next downstream buffer.
            """
            self.accept_event(event, channel_index)
            if event.final_event:
                if self.debug:
                    print(f'Downstream buffer {self.active_channels[channel_index]["buffer"].buffer_index} released at {self.env.now}')
                self.release_buffer(channel_index)

        else:
            """
            Not in active channel. Event is dropped. 
            """
            self.drop_event(event)
