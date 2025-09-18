from temscript import null_microscope
from temscript import microscope
TEM = microscope.Microscope()
goalangle = 1.1868238913561442
rotationspeed = 0.008523114687031229
TEM.set_stage_position(a=goalangle,method='GO',speed=rotationspeed)