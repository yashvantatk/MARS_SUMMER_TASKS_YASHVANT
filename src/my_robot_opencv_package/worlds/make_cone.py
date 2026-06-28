import math

# Dictionary of our exact RGB colors
colors = {
    'red': (1.0, 0.0, 0.0),
    'green': (0.0, 1.0, 0.0),
    'blue': (0.0, 0.0, 1.0),
    'yellow': (1.0, 1.0, 0.0),
    'orange': (1.0, 0.5, 0.0)
}

def create_cone(name, color, radius=0.1, height=0.4, segments=32):
    # 1. Forge the Material File (.mtl)
    with open(f"{name}_cone.mtl", 'w') as f:
        f.write(f"newmtl {name}Material\n")
        f.write(f"Kd {color[0]} {color[1]} {color[2]}\n") # Diffuse (The Color)
        f.write("Ka 1.0 1.0 1.0\n") # Ambient
        f.write("Ks 0.0 0.0 0.0\n") # Specular (No shiny glare)

    # 2. Forge the 3D Mesh (.obj)
    with open(f"{name}_cone.obj", 'w') as f:
        f.write(f"mtllib {name}_cone.mtl\n") # Link to the material file above!
        f.write(f"usemtl {name}Material\n")  # Apply the color
        
        # Vertices
        f.write(f"v 0 0 {height/2}\n")
        f.write(f"v 0 0 {-height/2}\n")
        for i in range(segments):
            angle = 2.0 * math.pi * i / segments
            x = radius * math.cos(angle)
            y = radius * math.sin(angle)
            f.write(f"v {x:.4f} {y:.4f} {-height/2}\n")

        # Normals
        f.write("vn 0.0000 0.0000 1.0000\n")
        f.write("vn 0.0000 0.0000 -1.0000\n")
        L = math.sqrt(height**2 + radius**2)
        for i in range(segments):
            angle = 2.0 * math.pi * i / segments
            nx = (math.cos(angle) * height) / L
            ny = (math.sin(angle) * height) / L
            f.write(f"vn {nx:.4f} {ny:.4f} {radius/L:.4f}\n")

        # Faces
        for i in range(segments):
            current = i + 3
            next_v = ((i + 1) % segments) + 3
            f.write(f"f 1//1 {current}//{current} {next_v}//{next_v}\n")
            f.write(f"f 2//2 {next_v}//2 {current}//2\n")

if __name__ == "__main__":
    for name, color in colors.items():
        create_cone(name, color)
        print(f"Forged {name}_cone.obj and {name}_cone.mtl")
