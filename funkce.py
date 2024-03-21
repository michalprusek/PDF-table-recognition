import cv2
import numpy as np
import matplotlib.pyplot as plt
from openpyxl import Workbook
from sklearn.cluster import KMeans
from pytesseract import image_to_string


def find_table_info(table_name, ref_data):
    # Find the row in ref_data where the name matches table_name
    match = ref_data[ref_data['name'] == table_name]

    if not match.empty:
        # Assuming 'ref_rows' and 'ref_cols' are column names in your Excel where the reference values are stored
        ref_rows = match['rows'].values[0]
        ref_cols = match['cols'].values[0]
        return ref_rows, ref_cols
    else:
        print(f"No match found for {table_name}")
        return None, None

def get_contour_centroid(contour):
    M = cv2.moments(contour)
    if M["m00"] != 0:
        cx = int(M["m10"] / M["m00"])
        cy = int(M["m01"] / M["m00"])
        return [cx, cy]  # Ensure this is a list or an array
    else:
        return [0, 0]


def save_to_excel(table_data, excel_path):
    # Create a workbook and select the active worksheet
    wb = Workbook()
    ws = wb.active

    # Iterate over the rows in the table data
    for row_idx, row in enumerate(table_data, start=1):  # Excel rows start at 1
        for col_idx, value in enumerate(row, start=1):  # Excel columns start at 1
            ws.cell(row=row_idx, column=col_idx).value = value

    # Save the workbook to the specified path
    wb.save(excel_path)


def sort_contours(contours, method="left-to-right"):
    # Initialize the reverse flag and sort index
    reverse = False
    i = 0
    # Handle if we need to sort in reverse
    if method == "right-to-left" or method == "bottom-to-top":
        reverse = True
    # Handle if we are sorting against the y-coordinate rather than the x-coordinate
    if method == "top-to-bottom" or method == "bottom-to-top":
        i = 1
    # Construct the list of bounding boxes and sort them from top to bottom
    boundingBoxes = [cv2.boundingRect(c) for c in contours]
    (contours, boundingBoxes) = zip(*sorted(zip(contours, boundingBoxes),
                                            key=lambda b: b[1][i], reverse=reverse))
    # Return the list of sorted contours and bounding boxes
    return (contours, boundingBoxes)


def extract_texts_from_cells(contours, image, num_rows, num_columns):
    # Sort the contours to correspond with the layout of the cells in the table
    contours, boundingBoxes = sort_contours(contours, method="top-to-bottom")

    # Use KMeans to cluster the y-values of the bounding boxes
    # to understand which row each bounding box is in
    centroids = KMeans(n_clusters=num_rows)
    rows = centroids.fit_predict([[y] for (x, y, w, h) in boundingBoxes])

    # Sort bounding boxes in each row
    table_data = []
    for row in range(num_rows):
        # Extract the contours in the current row
        row_contours = [contours[i] for i in range(len(contours)) if rows[i] == row]
        row_boundingBoxes = [boundingBoxes[i] for i in range(len(boundingBoxes)) if rows[i] == row]

        # Sort the contours in this row from left to right
        row_contours, row_boundingBoxes = sort_contours(row_contours, method="left-to-right")

        # Extract text from each sorted contour
        row_text = []
        for c in row_contours:
            x, y, w, h = cv2.boundingRect(c)
            cell_img = image[y:y + h, x:x + w]
            text = image_to_string(cell_img, lang='ces', config='--psm 6').strip()
            row_text.append(text)

        # Append to table_data
        table_data.append(row_text)

    # Check if any row is shorter than the number of columns and pad it
    for row in table_data:
        if len(row) < num_columns:
            row.extend([""] * (num_columns - len(row)))

    return table_data


def count_grid_lines(lines):
    # Define the kernels for horizontal and vertical lines
    horizontal_lines, vertical_lines = find_table_structure(lines)

    # Find contours of the lines
    contours_horizontal, _ = cv2.findContours(horizontal_lines, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contours_vertical, _ = cv2.findContours(vertical_lines, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Count the number of horizontal and vertical lines
    num_rows = len(contours_horizontal) -1
    num_columns = len(contours_vertical) -1

    return num_rows, num_columns


def extend_to_edges(x1, y1, x2, y2, width, height):
    if abs(x1 - x2) < 3:  # Vertical line
        return x1, 0, x2, height
    elif abs(y1 - y2) < 3:  # Horizontal line
        return 0, y1, width, y2
    else:
        return x1, y1, x2, y2


def plot_hough_histogram(lines, min_angle=-90, max_angle=90, bin_size=1):
    # Úhly v stupních
    angles = np.rad2deg([line[0][1] for line in lines])

    # Vytvoření histogramu
    bins = np.arange(min_angle, max_angle, bin_size)
    hist, bins = np.histogram(angles, bins=bins)

    # Vykreslení histogramu
    plt.figure()
    plt.bar(bins[:-1], hist, width=bin_size, edgecolor='black')
    plt.title('Histogram Houghovy transformace')
    plt.xlabel('Úhel (stupně)')
    plt.ylabel('Počet přímek')
    plt.xlim(min_angle, max_angle)
    plt.grid(True)
    plt.show()


def detect_and_draw_lines(table, threshold, min_line_lenght, rho_resolution=0.5, theta_resolution=np.pi / 360):
    table_shape = table.shape
    # Adjusted Hough Transform parameters for better accuracy
    lines = cv2.HoughLinesP(table, rho_resolution, theta_resolution, threshold, minLineLength=min_line_lenght)

    line_img = np.zeros_like(table)

    if lines is not None:
        for line in lines:
            for x1, y1, x2, y2 in line:
                x1_ext, y1_ext, x2_ext, y2_ext = extend_to_edges(x1, y1, x2, y2, table_shape[1], table_shape[0])
                cv2.line(line_img, (x1_ext, y1_ext), (x2_ext, y2_ext), (255, 255, 255), 1)
    else:
        print("No lines were detected.")

    return line_img


def order_points(pts):
    # Initialize a list of coordinates that will be ordered
    # such that the first entry in the list is the top-left,
    # the second entry is the top-right, the third is the
    # bottom-right, and the fourth is the bottom-left
    rect = np.zeros((4, 2), dtype="float32")

    # The top-left point will have the smallest sum, whereas
    # the bottom-right point will have the largest sum
    s = pts.sum(axis=1)
    rect[0] = pts[np.argmin(s)]
    rect[2] = pts[np.argmax(s)]

    # Now, compute the difference between the points, the
    # top-right point will have the smallest difference,
    # whereas the bottom-left will have the largest difference
    diff = np.diff(pts, axis=1)
    rect[1] = pts[np.argmin(diff)]
    rect[3] = pts[np.argmax(diff)]

    # Return the ordered coordinates
    return rect


def apply_perspective_transform(cropped_table, cropped_img, src_points):
    # First, order the source points
    src_points_ordered = order_points(src_points)

    height, width = cropped_table.shape[:2]
    dst_points = np.array([
        [0, 0],
        [width - 1, 0],
        [width - 1, height - 1],
        [0, height - 1]
    ], dtype='float32')

    # Compute the perspective transform matrix using ordered source points
    matrix = cv2.getPerspectiveTransform(src_points_ordered, dst_points)
    warped_img = cv2.warpPerspective(cropped_img, matrix, (width, height))
    warped_table = cv2.warpPerspective(cropped_table, matrix, (width, height))
    return warped_table, warped_img


def extract_text_by_contours(contours, image):
    text_and_coords = []
    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)
        cropped_img = image[y:y + h, x:x + w]
        text = image_to_string(cropped_img, lang='ces', config='--psm 6').strip()
        text_and_coords.append((text, x))
    return text_and_coords


def sort_contours_by_y(contours):
    bounding_boxes = [cv2.boundingRect(contour) for contour in contours]  # Získání bounding boxů
    contours_with_boxes = zip(contours, bounding_boxes)
    sorted_contours_with_boxes = sorted(contours_with_boxes, key=lambda x: x[1][1])  # Seřazení podle y
    sorted_contours = [contour for contour, _ in sorted_contours_with_boxes]
    return sorted_contours

def find_table_structure(img_binary):
    horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (40, 1))
    vertical_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 30))
    horizontal_lines = cv2.morphologyEx(img_binary, cv2.MORPH_OPEN, horizontal_kernel, iterations=2)
    vertical_lines = cv2.morphologyEx(img_binary, cv2.MORPH_OPEN, vertical_kernel, iterations=2)

    return horizontal_lines, vertical_lines
