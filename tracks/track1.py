outer_walls = [
    (100, 100), (200, 50), (400, 50), (550, 100), (600, 200), # Start straight and first corner
    (650, 300), (600, 400), (550, 450), # Top curve and straight
    (400, 500), (250, 500), (200, 450), # Bottom left corner
    (150, 350), (100, 300), (50, 200), # S-curve at bottom
    (100, 150), (100, 100) # Back to start
]
    
inner_walls = [
    (200, 150), (300, 100), (400, 100), (500, 150), (550, 200), # Inner start section
    (575, 250), (550, 300), (500, 350), # Top inner S-curve
    (400, 400), (300, 400), (250, 350), # Bottom left straight
    (200, 300), (150, 250), (200, 200), # Inner curve at bottom
    (200, 150) # Back to inner start
]

car_start = (150, 180)