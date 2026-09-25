from datetime import datetime


# In-memory conversation history
conversation_history = []


def add_history(
    query,
    intent,
    location,
    response
):
    """
    Store one conversation entry in memory.
    """

    entry = {
        "query": query,
        "intent": intent,
        "location": location,
        "response": response,
        "timestamp": datetime.now().isoformat()
    }

    conversation_history.append(entry)

    return entry


def get_history():
    """
    Return all conversation history.
    """

    return conversation_history


def clear_history():
    """
    Clear conversation history.
    """

    conversation_history.clear()

    return {
        "message": "Conversation history cleared"
    }