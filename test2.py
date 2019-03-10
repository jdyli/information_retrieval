from CoorAscent import CoordinateAscent


def e(params):  # Objective function
    # Minimize (x+1)^2 + (y+10)^2 + (z+100)^2 where -50 <= z
    if not -50 <= params['z']:
        return None  # For invalid parameter values
    return -((params['x'] + 1) ** 2 + (params['y'] + 10) ** 2 + (params['z'] + 100) ** 2)


params = {'x': 1.0, 'y': 23.0, 'z': 456.0}  # Arbitrary initial values

print(CoordinateAscent(e).learn(params))  # => {'x': -1.0, 'y': -10.0, 'z': -50.0}
