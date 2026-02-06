from langchain_community.chat_message_histories import ChatMessageHistory

memory_store = {}

def get_memory(cid):
    return memory_store.setdefault(cid, ChatMessageHistory())
