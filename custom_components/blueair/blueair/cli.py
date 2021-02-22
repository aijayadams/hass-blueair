"""This module contains the Blueair command line client."""

import argparse
import coloredlogs  # type: ignore
import logging
import matplotlib
import matplotlib.pyplot as pyplot
import pandas as pd
import tzlocal

from datetime import datetime, timedelta, timezone
from itertools import chain, groupby
from time import sleep
from typing import Any, Dict, Sequence, List

from .blueair import BlueAir
from .database import Database

logger = logging.getLogger(__name__)

def _tabularize(it: Sequence[Dict[str, Any]], titles: List[str], field_keys: List[str]) -> None:
    # Get maximum string lengths per dict key
    grouped = groupby(sorted(chain(*(i.items() for i in it)), key=lambda x: x[0]), lambda x: x[0])
    lengths = {k: max(len(str(w)) for _, w in v) for k, v in grouped}

    title_mapping = dict(zip(field_keys, titles))
    lengths = {k: max(v, len(title_mapping[k])) for k, v in lengths.items()}

    print("  ".join(title.ljust(lengths[field]) for title, field in zip(titles, field_keys)))
    print("  ".join("-" * lengths[field] for field in field_keys))

    for entry in it:
        print("  ".join(str(entry[field]).ljust(lengths[field]) for field in field_keys))

def _collect_measurements(blueair: BlueAir, database: Database, device_uuid: str) -> None:
    now = datetime.now(timezone.utc)
    start_timestamp = database.get_latest_timestamp() or int((now - timedelta(days=10)).timestamp())
    end_timestamp = int(now.timestamp())
    measurements = blueair.get_data_points_between(device_uuid, start_timestamp + 1, end_timestamp)

    for measurement in measurements:
        database.insert_measurement(**measurement)

    database.commit()

    logger.info(f"Collected {len(measurements)} new measurements")

def _plot_measurements(database: Database, filename: str) -> None:
    measurements = database.get_all_measurements()

    # get the local timezone
    zone = tzlocal.get_localzone().zone

    # Create a dataframe for plotting
    dataframe = pd.DataFrame(measurements)
    dataframe["timestamp"] = dataframe["timestamp"].apply(lambda timestamp: datetime.utcfromtimestamp(timestamp))
    dataframe["timestamp"] = dataframe["timestamp"].dt.tz_localize("UTC").dt.tz_convert(zone)  # type: ignore

    matplotlib.rcParams["timezone"] = zone  # type: ignore
    pyplot.style.use("bmh")  # type: ignore

    fig, axs = pyplot.subplots(4, 1, figsize=(10, 10), constrained_layout=True)  # type: ignore

    axs[0].plot(dataframe["timestamp"], dataframe["pm25"])
    axs[0].set_title("PM 2.5")
    axs[0].set_ylabel("ug/m3")
    axs[0].set_ylim(bottom=0)
    axs[0].set_facecolor("#ffffff")
    axs[0].margins(x=0.01, y=0.1)

    axs[0].axhspan(0, 10, facecolor="#8AE3CE40")
    axs[0].axhspan(10, 20, facecolor="#D1E5A840")
    axs[0].axhspan(20, 35, facecolor="#FEDC9A40")
    axs[0].axhspan(35, 80, facecolor="#FAC07E40")
    axs[0].axhspan(80, 1000, facecolor="#FA897E40")

    locator = matplotlib.dates.AutoDateLocator()  # type: ignore
    axs[0].get_xaxis().set_major_locator(locator)
    axs[0].get_xaxis().set_major_formatter(matplotlib.dates.ConciseDateFormatter(locator))  # type: ignore

    axs[1].plot(dataframe["timestamp"], dataframe["voc"])
    axs[1].sharex(axs[0])
    axs[1].set_title("VOC")
    axs[1].set_ylabel("ppb")
    axs[1].set_ylim(bottom=0)
    axs[1].set_facecolor("#ffffff")
    axs[1].margins(x=0.01, y=0.1)

    axs[1].axhspan(0, 200, facecolor="#8AE3CE40")
    axs[1].axhspan(200, 400, facecolor="#D1E5A840")
    axs[1].axhspan(400, 600, facecolor="#FEDC9A40")
    axs[1].axhspan(600, 800, facecolor="#FAC07E40")
    axs[1].axhspan(800, 10000, facecolor="#FA897E40")

    axs[2].plot(dataframe["timestamp"], dataframe["temperature"])
    axs[2].sharex(axs[0])
    axs[2].set_title("Temperature")
    axs[2].set_ylabel("C")
    axs[2].margins(x=0.01, y=0.1)

    axs[3].plot(dataframe["timestamp"], dataframe["humidity"])
    axs[3].sharex(axs[0])
    axs[3].set_title("Relative Humidity")
    axs[3].set_ylabel("%")
    axs[3].margins(x=0.01, y=0.1)

    pyplot.savefig(filename)
    pyplot.show()

def run() -> None:
    """Run the Blueair command line client."""
    # Create argument parser
    parser = argparse.ArgumentParser(description="An example application using the Python BlueAir client that collects and graphs measurements.")
    parser.add_argument("--email", help="The username for the BlueAir account")
    parser.add_argument("--password", help="The password for the BlueAir acount")
    parser.add_argument("--list-devices", action="store_true", help="List the available devices for the account and exit")
    parser.add_argument("--list-attributes", action="store_true", help="List the available attributes for the device and exit")
    parser.add_argument("--uuid", help="The device UUID to use for collecting measurements")
    parser.add_argument("--interval", type=int, metavar="N", help="Collect measurements every N seconds")
    parser.add_argument("--output", default="chart.png", help="The filename to use for the generated chart (defaults to chart.png)")
    parser.add_argument("--database", default="blueair.db", help="The filename to use for the SQLite database (defaults to blueair.db)")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose logging")

    args = parser.parse_args()

    # Configure logger
    coloredlogs.install(
        level=args.verbose and logging.INFO or logging.WARNING,
        fmt="%(asctime)s %(name)s[%(process)d] %(levelname)s %(message)s"
    )

    if not args.email or not args.password:
        raise RuntimeError("Must provide both email and password")

    blueair = BlueAir(args.email, args.password)

    # Handle device list mode
    if args.list_devices:
        devices = blueair.get_devices()

        _tabularize(
            devices,
            ["UUID", "User ID", "MAC Address", "Device Name"],
            ["uuid", "userId", "mac", "name"]
        )

        exit()

    # Get UUID or fetch from device list if not specified
    uuid = args.uuid

    if not uuid:
        devices = blueair.get_devices()
        if not devices:
            raise RuntimeError("No devices found")
        elif len(devices) != 1:
            raise RuntimeError("Found multiple devices, use --uuid argument to specify which one to use")
        else:
            uuid = devices[0]["uuid"]

    # Handle attributes list mode
    if args.list_attributes:
        for key, value in blueair.get_attributes(uuid).items():
            print(f"{key}: {value}")

        exit()

    # Initialize database session
    database = Database(filename=args.database)

    # Loop if interval is specified
    if args.interval:
        while True:
            logger.info("Collecting measurements")
            _collect_measurements(blueair, database, uuid)

            logger.info("Generating chart")
            _plot_measurements(database, args.output)

            logger.info(f"Waiting {args.interval} seconds")
            sleep(args.interval)
    else:
        logger.info("Collecting measurements")
        _collect_measurements(blueair, database, uuid)

        logger.info("Generating chart")
        _plot_measurements(database, args.output)
