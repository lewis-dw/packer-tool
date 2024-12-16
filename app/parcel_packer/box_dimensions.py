import itertools
import numpy as np
import plotly.graph_objects as go
import plotly.express as px

def find_best_fitting_box(packed_box_dimensions, available_boxes):
    min_wasted_volume = float("inf")
    best_box = None

    for box in available_boxes:
        if all(box_dim >= packed_dim for box_dim, packed_dim in zip(box, packed_box_dimensions)):
            wasted_volume = (
                (box[0] * box[1] * box[2])
                - (packed_box_dimensions[0] * packed_box_dimensions[1] * packed_box_dimensions[2])
            )
            if wasted_volume < min_wasted_volume:
                min_wasted_volume = wasted_volume
                best_box = box

    return best_box


def can_place(pos, product, packed_items, packed_box):
    x, y, z = pos

    # Generate rotations that minimize height
    rotations = get_rotations_minimize_height(product)

    for rotated_product in rotations:
        dx, dy, dz = rotated_product
        if (
            x + dx <= packed_box[0]
            and y + dy <= packed_box[1]
            and z + dz <= packed_box[2]
        ):
            new_item = {"position": (x, y, z), "dimensions": (dx, dy, dz)}
            if not has_intersection(new_item, packed_items):
                return new_item

    return None


def has_intersection(item1, items):
    for item2 in items:
        if (
            item1["position"][0] < item2["position"][0] + item2["dimensions"][0]
            and item1["position"][0] + item1["dimensions"][0] > item2["position"][0]
            and item1["position"][1] < item2["position"][1] + item2["dimensions"][1]
            and item1["position"][1] + item1["dimensions"][1] > item2["position"][1]
            and item1["position"][2] < item2["position"][2] + item2["dimensions"][2]
            and item1["position"][2] + item1["dimensions"][2] > item2["position"][2]
        ):
            return True
    return False


def get_possible_positions(packed_items, product, packed_box):
    possible_positions = []

    if not packed_items:
        possible_positions.append((0, 0, 0))
    else:
        # Generate positions at all levels and orientations
        for item in packed_items:
            positions = [
                # Beside in x-direction
                (item["position"][0] + item["dimensions"][0], item["position"][1], item["position"][2]),
                # Beside in y-direction
                (item["position"][0], item["position"][1] + item["dimensions"][1], item["position"][2]),
                # On top in z-direction
                (item["position"][0], item["position"][1], item["position"][2] + item["dimensions"][2]),
            ]

            for pos in positions:
                if (
                    pos[0] + min(product) <= packed_box[0]
                    and pos[1] + min(product) <= packed_box[1]
                    and pos[2] + min(product) <= packed_box[2]
                ):
                    possible_positions.append(pos)

    # Remove duplicate positions
    possible_positions = list(set(possible_positions))

    # Sort positions to prioritize lower z-values and positions where the item can lay flat
    possible_positions.sort(key=lambda position: (position[2], position[0] + position[1]))

    return possible_positions


def get_rotations_minimize_height(product):
    # Find the smallest dimension
    min_dim = min(product)
    # Get all permutations of the product dimensions
    permutations = set(itertools.permutations(product))
    rotations = []

    # Generate rotations where the smallest dimension is assigned to dz (height)
    for perm in permutations:
        dims = list(perm)
        min_index = dims.index(min_dim)
        # Swap the smallest dimension to index 2 (dz)
        dims[2], dims[min_index] = dims[min_index], dims[2]
        rotations.append(tuple(dims))

    # Remove duplicates
    rotations = list(set(rotations))

    # Sort rotations by height (smallest dz)
    rotations.sort(key=lambda dims: dims[2])

    return rotations


def pack_products(products, available_boxes):
    # Sort available boxes by volume (ascending)
    available_boxes = sorted(available_boxes, key=lambda box: box[0] * box[1] * box[2])

    # Determine the median volume to separate large and small items
    volumes = [p[0] * p[1] * p[2] for p in products]
    median_volume = np.median(volumes)

    # Separate products into large and small items
    large_items = [p for p in products if p[0] * p[1] * p[2] >= median_volume]
    small_items = [p for p in products if p[0] * p[1] * p[2] < median_volume]

    # Sort large items by volume descending, then by height ascending
    large_items.sort(key=lambda p: (-p[0] * p[1] * p[2], p[2]))
    # Sort small items by volume descending, then by height ascending
    small_items.sort(key=lambda p: (-p[0] * p[1] * p[2], p[2]))

    for box in available_boxes:
        packed_items = []
        packed_box = box

        # First pass: Place large items
        for product in large_items:
            positions = get_possible_positions(packed_items, product, packed_box)

            placed = False
            for pos in positions:
                item = can_place(pos, product, packed_items, packed_box)
                if item is not None:
                    packed_items.append(item)
                    placed = True
                    break

            if not placed:
                break  # Cannot place this product in the box, try next box

        # If not all large items are placed, continue to next box
        if len(packed_items) < len(large_items):
            continue

        # Second pass: Place small items
        for product in small_items:
            positions = get_possible_positions(packed_items, product, packed_box)

            placed = False
            for pos in positions:
                item = can_place(pos, product, packed_items, packed_box)
                if item is not None:
                    packed_items.append(item)
                    placed = True
                    break

            if not placed:
                break  # Cannot place this product in the box, try next box

        # If all items are placed, finalize the packing
        if len(packed_items) == len(products):
            # Calculate the used dimensions
            packed_box_dimensions = (
                max(item["position"][0] + item["dimensions"][0] for item in packed_items),
                max(item["position"][1] + item["dimensions"][1] for item in packed_items),
                max(item["position"][2] + item["dimensions"][2] for item in packed_items),
            )

            best_box = find_best_fitting_box(packed_box_dimensions, available_boxes)
            if best_box:
                # Adjust the box dimensions to match the packed items (cut down the height)
                adjusted_box = (
                    best_box[0],
                    best_box[1],
                    packed_box_dimensions[2],
                )
                return adjusted_box, packed_items

    return None, None


def draw_packed_items(packed_items, packed_box_dimensions):
    fig = go.Figure()

    # Add the box edges
    box_x, box_y, box_z = packed_box_dimensions
    fig.add_trace(go.Mesh3d(
        x=[0, box_x, box_x, 0, 0, box_x, box_x, 0],
        y=[0, 0, box_y, box_y, 0, 0, box_y, box_y],
        z=[0, 0, 0, 0, box_z, box_z, box_z, box_z],
        i=[0, 1, 2, 3, 4, 5, 6, 7, 0, 3, 4, 7],
        j=[1, 2, 3, 0, 5, 6, 7, 4, 4, 7, 5, 6],
        k=[2, 3, 0, 1, 6, 7, 4, 5, 5, 6, 1, 2],
        opacity=0.1,
        color='gray',
        flatshading=True,
        name='Box'
    ))

    # Generate a list of colors for the items
    colors = px.colors.qualitative.Alphabet
    color_index = 0

    for idx, packed_item in enumerate(packed_items):
        x0, y0, z0 = packed_item["position"]
        dx, dy, dz = packed_item["dimensions"]

        # Define the vertices of the cuboid
        x = [x0, x0 + dx, x0 + dx, x0, x0, x0 + dx, x0 + dx, x0]
        y = [y0, y0, y0 + dy, y0 + dy, y0, y0, y0 + dy, y0 + dy]
        z = [z0, z0, z0, z0, z0 + dz, z0 + dz, z0 + dz, z0 + dz]

        # Define the faces of the cuboid
        faces = [
            [0, 1, 2, 3],  # Bottom face
            [4, 5, 6, 7],  # Top face
            [0, 1, 5, 4],  # Front face
            [1, 2, 6, 5],  # Right face
            [2, 3, 7, 6],  # Back face
            [3, 0, 4, 7],  # Left face
        ]

        # Flatten the face indices for Plotly
        i = []
        j = []
        k = []
        for face in faces:
            i.extend([face[0], face[0], face[0]])
            j.extend([face[1], face[2], face[3]])
            k.extend([face[2], face[3], face[0]])

        # Assign a color to each item
        color = colors[color_index % len(colors)]
        color_index += 1

        fig.add_trace(go.Mesh3d(
            x=x,
            y=y,
            z=z,
            i=i,
            j=j,
            k=k,
            color=color,
            opacity=0.8,
            flatshading=True,
            name=f'Item {idx + 1}',
            hovertext=f'Item {idx + 1}<br>Position: {packed_item["position"]}<br>Dimensions: {packed_item["dimensions"]}',
            hoverinfo='text',
            showscale=False
        ))

    # Set the layout
    fig.update_layout(
        scene=dict(
            xaxis=dict(range=[0, box_x], backgroundcolor="white"),
            yaxis=dict(range=[0, box_y], backgroundcolor="white"),
            zaxis=dict(range=[0, box_z], backgroundcolor="white"),
            aspectmode='data',
            camera=dict(eye=dict(x=1.25, y=1.25, z=1.25))
        ),
        width=800,
        height=600,
        title='Packed Items Visualization',
        showlegend=True
    )

    fig.show()

def draw_box_edges(ax, box_dimensions):
    # Draw the edges of the box
    x, y, z = box_dimensions
    r = [0, x]
    s = [0, y]
    t = [0, z]

    # Create combinations of points
    for s, e in itertools.combinations(np.array(list(itertools.product(r, s, t))), 2):
        if np.sum(np.abs(s - e) == np.array(box_dimensions)) == 2:
            ax.plot3D(*zip(s, e), color="black")


# Example usage
products = [
    (1, 5, 5),
    (8, 5, 2),
    (5, 5, 8),
    (4, 3, 2),
    (4, 8, 2),
    (4, 4, 4),
    (9, 2, 2)
]

available_boxes = [
    (8, 8, 8),
    (10, 10, 10),
    (15, 15, 12),
    (15, 15, 15),
    (20, 20, 20),
    (25, 25, 25),
    (30, 30, 30),
]

result, packed_items = pack_products(products, available_boxes)
if result:
    adjusted_box = result
    print("The most efficient box to use is:", adjusted_box)
    draw_packed_items(packed_items, adjusted_box)
else:
    print("No box found that can accommodate all items without intersection.")
