import asyncio
import json

from adapters.repositories.receiver import MongoReceiverRepository
from adapters.repositories.source import MongoSourceRepository
from adapters.repositories.stream import MongoStreamRepository
from container import container
from domain.models import Receiver, Source, Stream


async def main():
    with open("streams.json") as f:
        streams_data = json.load(f)

    streams = []
    receivers = []
    sources = []
    for stream in streams_data:
        source = Source(
            name=stream["source"]["name"],
            slug=stream["source"]["slug"],
            fetcher_type=stream["source"]["fetcher_type"],
            fetcher_options=stream["source"]["fetcher_options"],
            parser_type=stream["source"]["parser_type"],
            parser_options=stream["source"]["parser_options"],
            tags=stream["source"]["tags"],
        )
        receiver = Receiver(
            name=stream["receiver"]["name"],
            slug=stream["receiver"]["slug"],
            type=stream["receiver"]["type"],
            options=stream["receiver"]["options"],
            options_allowed_to_override=["disable_link_preview"],
        )
        stream = Stream(
            slug=f"{source.slug}-to-{receiver.slug}",
            intervals=["*/10 * * * *"],
            squash=stream["squash"],
            receiver_options_override=stream["receiver_options_override"],
            message_template=stream["message_template"] or stream["receiver"]["message_template"],
            modifiers=stream["modifiers"],
            active=True,
            source_slug=source.slug,
            receiver_slug=receiver.slug,
        )
        streams.append(stream)
        if receiver not in receivers:
            receivers.append(receiver)
        if source not in sources:
            sources.append(source)

    mongo_db = container.mongo_client().get_database()
    receiver_repo = MongoReceiverRepository(mongo_db)
    source_repo = MongoSourceRepository(mongo_db)
    stream_repo = MongoStreamRepository(mongo_db)

    for receiver in receivers:
        await receiver_repo.add(receiver)

    for source in sources:
        await source_repo.add(source)

    for stream in streams:
        await stream_repo.add(stream)


if __name__ == "__main__":
    asyncio.run(main())
