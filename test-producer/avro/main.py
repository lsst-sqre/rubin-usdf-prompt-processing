import logging
import json
import os
import sys
import socket
import asyncio
import typing

import enum
import random

from aiokafka import AIOKafkaProducer
from dataclasses import dataclass
from dataclasses_avroschema import AvroModel


logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

# kafka_cluster = os.environ["KAFKA_CLUSTER"]
# kafka_cluster = "127.0.0.1:46315"
kafka_cluster = "34.123.148.90:9094"
# topic = os.environ["BUCKET_NOTIFY_TOPIC"]
topic = "next_visit_avro_topic"
# msg_batch_size = os.environ["MSG_BATCH_SIZE"]
msg_batch_size = 1


class Instrument(enum.Enum):
    LATISS = "LATISS"
    LSSTCOMCAM = "LSSTComCam"
    LSSTCAM = "LSSTCam"


@dataclass
class NextVisitModel(AvroModel):
    "Next Visit Message"
    salIndex: int
    scriptSalIndex: int
    groupId: str
    nimages: int
    filters: str
    coordinateSystem: int
    position: typing.List[int]
    rotationSystem: int
    cameraAngle: int
    survey: str
    dome: int
    duration: int
    totalCheckpoints: int


def acked(err, msg):
    if err is not None:
        logging.error("Failed to deliver message: %s: %s", msg.value(), err)
    else:
        logging.info("Message produced: %s", msg.value())


async def send(loop, total_events=3):
    producer = AIOKafkaProducer(loop=loop, bootstrap_servers=kafka_cluster)
    # Get cluster layout and initial topic/partition leadership information
    await producer.start()

    for event_number in range(1, total_events + 1):
        # Produce message
        print(f"Sending event number {event_number}")

        position_list = [0.0, 0.0]

        next_visit = NextVisitModel(
            salIndex=random.randint(1, 2),
            scriptSalIndex=random.randint(1, 2),
            groupId=random.choice(
                ["visit-12882-20221027", "visit-12882-20221028", "visit-12882-20221029"]
            ),
            nimages=random.randint(1, 3),
            filters=random.choice(["k1234", "k1235", "k1236"]),
            coordinateSystem=random.randint(1, 3),
            position=position_list,
            rotationSystem=random.randint(1, 3),
            cameraAngle=random.randint(1, 3),
            survey=random.choice(["k1234", "k1235", "k1236"]),
            dome=random.randint(1, 3),
            duration=random.randint(1, 3),
            totalCheckpoints=random.randint(1, 3),
        )

        # create the message
        message = next_visit.serialize()

        await producer.send_and_wait(topic, message)
        # sleep for 2 seconds
        await asyncio.sleep(2)
    else:
        # Wait for all pending messages to be delivered or expire.
        await producer.stop()
        print("Stoping producer...")


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    tasks = asyncio.gather(send(loop))

    loop.run_until_complete(tasks)
