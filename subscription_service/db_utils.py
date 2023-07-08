from telethon.tl.functions.channels import JoinChannelRequest, LeaveChannelRequest


async def subscribe_to_channel(client, channel_username):
    channel_entity = await client.get_input_entity(channel_username)
    await client(JoinChannelRequest(channel=channel_entity))


async def unsubscribe_from_channel(client, channel_username):
    channel_entity = await client.get_input_entity(channel_username)
    await client(LeaveChannelRequest(channel=channel_entity))
