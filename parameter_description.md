Scintillator -> integrator -> ring buffer -> MUX1 -> long buffer ->MUX -> Digitizer


configuration model design parameters:
*The parameters which change the actual architecture of the simulator*
- num_SnH_ring_buff: Number of S&H units in ring buffers
- num_channels: number of front end channels
- num_SnH_long_buff: number of S&H units in long tail buffers
- num_long_buffs: number of long tail buffers
- num_of_digitizers: number of digitizers
- amux_associativity: description of how the connections in the amux  can be routed. TBD , currently not used. 


configuration model constants:
*The parameters which define the constant values based on real world models*
- short_SnH_delay: Short S&H unit delay length 
- long_SnH_delay: Long S&H unit delay length
- mux0_delay: delay length of delay introduced by the first MUX
- mux1_delay: delay length of delay introduced by the Second MUX
- integrator_delay: delay length of the integrator( This also sets the granularity of the waveform resolution, since the gate delays will be much shorter the integrator delay this parameter combines both values)