import csv
import argparse
import xml.etree.ElementTree as ET
from xml.dom import minidom


def pretty_xml(element):
    rough = ET.tostring(element, encoding="utf-8")
    parsed = minidom.parseString(rough)
    return parsed.toprettyxml(indent="  ")


def clean_text(value):
    if value is None:
        return ""
    return value.strip()


def extract_event_title(full_event_label, event_id):
    """
    Example:
    'Event  37   Girls 100 Meter Hurdles C'
    becomes:
    'Girls 100 Meter Hurdles C'
    """
    text = clean_text(full_event_label)

    prefix = f"Event  {event_id}"
    if text.startswith(prefix):
        return text[len(prefix):].strip()

    prefix = f"Event {event_id}"
    if text.startswith(prefix):
        return text[len(prefix):].strip()

    return text


def csv_to_viz_xml(input_csv, output_xml, max_rows_per_event=9):
    events = {}

    with open(input_csv, "r", encoding="utf-8-sig", newline="") as file:
        reader = csv.reader(file)

        header = next(reader, None)

        for row in reader:
            if len(row) < 5:
                continue

            full_event_label = clean_text(row[0])
            event_id = clean_text(row[1])
            lane = clean_text(row[2])
            name = clean_text(row[3])
            school = clean_text(row[4])

            if not event_id:
                continue

            if event_id not in events:
                events[event_id] = {
                    "title": extract_event_title(full_event_label, event_id),
                    "rows": []
                }

            events[event_id]["rows"].append({
                "lane": lane,
                "name": name,
                "school": school
            })

    root = ET.Element("viz_data")

    for event_id, event_data in events.items():
        prefix = "E" + event_id

        title_node = ET.SubElement(root, f"{prefix}_event_title")
        title_node.text = event_data["title"]

        rows = event_data["rows"][:max_rows_per_event]

        for i in range(1, max_rows_per_event + 1):
            if i <= len(rows):
                row_data = rows[i - 1]
                lane = row_data["lane"]
                name = row_data["name"]
                school = row_data["school"]
            else:
                lane = ""
                name = ""
                school = ""

            lane_node = ET.SubElement(root, f"{prefix}_lane_{i}")
            lane_node.text = lane

            name_node = ET.SubElement(root, f"{prefix}_name_{i}")
            name_node.text = name

            school_node = ET.SubElement(root, f"{prefix}_school_{i}")
            school_node.text = school

    with open(output_xml, "w", encoding="utf-8") as file:
        file.write(pretty_xml(root))

    print(f"Created XML: {output_xml}")
    print(f"Events found: {len(events)}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Convert LHSAA track CSV heat sheet data into flat Viz XML fields."
    )

    parser.add_argument("input_csv", help="Input CSV file")
    parser.add_argument("output_xml", help="Output XML file")

    args = parser.parse_args()

    csv_to_viz_xml(args.input_csv, args.output_xml)
