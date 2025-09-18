from temscript import null_microscope
from temscript import microscope
TEM = microscope.Microscope()
goalangle = 0.17453292519943295
rotationspeed = 0.017046229374062458
TEM.set_stage_position(a=goalangle,method='GO',speed=rotationspeed)