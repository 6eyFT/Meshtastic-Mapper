import pandas as pd


def parse_csv_file(filepath):
    points = []
    try:
        df = pd.read_csv(filepath)

        for index, row in df.iterrows():
            if pd.notnull(row["sender lat"]) and pd.notnull(row["sender long"]):
                point = {
                    "lat": float(row["sender lat"]),
                    "lon": float(row["sender long"]),
                    "node_id": str(row["from"]),
                    "sender_name": (
                        str(row["sender name"])
                        if pd.notnull(row["sender name"])
                        else "Unknown"
                    ),
                    "snr": float(row["rx snr"]) if pd.notnull(row["rx snr"]) else 0,
                    "distance": (
                        float(row["distance"]) if pd.notnull(row["distance"]) else 0
                    ),
                    "time": (
                        f"{row['date']} {row['time']}"
                        if pd.notnull(row["date"]) and pd.notnull(row["time"])
                        else "Unknown"
                    ),
                }
                points.append(point)

    except Exception as e:
        print(f"Error parsing CSV: {e}")

    return points
