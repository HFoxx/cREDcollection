from temscript import null_microscope
from temscript import microscope
TEM = microscope.Microscope()
goalangle = 0.3490658503988659
rotationspeed = 0.006818491749624983
TEM.set_stage_position(a=goalangle, method='GO', speed=rotationspeed)
