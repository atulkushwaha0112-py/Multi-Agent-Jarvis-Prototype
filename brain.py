from mistralai import Mistral
from dotenv import load_dotenv
import os
import json


from read_emails import get_recent_emails
from memory import search_memory, save_memory, search_emails
from gmail_auth import get_gmail_service

load_dotenv()

MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")
client = Mistral(api_key=MISTRAL_API_KEY)


MODEL = "mistral-large-latest"

# Yahan hum LLM ko batate hain uske paas kaunse "tools" (functions) hain
tools = [
    {
        "type": "function",
        "function": {
            "name": "check_inbox",
            "description": "Recent/naye emails inbox se laata hai",
            "parameters": {
                "type": "object",
                "properties": {
                    "count": {
                        "type": "integer",
                        "description": "Kitne emails chahiye, default 5"
                    }
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_memory",
            "description": "Contact ya koi bhi saved fact (jaise kisi ka email address) memory mein dhoondta hai",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Kya dhoondhna hai, jaise ek naam"
                    }
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "save_memory",
            "description": "Naya fact yaad rakhne ke liye save karta hai, jaise kisi ka email address",
            "parameters": {
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string",
                        "description": "Jo fact save karna hai"
                    }
                },
                "required": ["text"]
            }
        }
    }
    {
        "type": "function",
        "function": {
            "name": "search_emails",
            "description": "Purane emails mein se content/topic ke basis pe dhoondta hai (jaise 'payment wala mail dhundo')",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Kya topic/content dhoondhna hai email mein"
                    }
                },
                "required": ["query"]
            }
        }
    }
]

# Function names ko actual Python functions se map karo
available_functions = {
    "check_inbox": lambda count=5: get_recent_emails(count),
    "search_memory": lambda query: search_memory(query),
    "save_memory": lambda text: save_memory(text),
    "search_emails": lambda query: search_emails(query)
}

def ask_brain(user_message):
    """
    User ki command leta hai, LLM ko deta hai,
    LLM decide karta hai kaunsa function call karna hai,
    aur final jawab return karta hai
    """
    messages = [
        {
            "role": "system",
            "content": "Tum ek email assistant ho. User voice se command dega. Tumhe decide karna hai kaunsa tool use karna hai. Jawab hamesha short aur clear do, jaise koi assistant bolta hai."
        },
        {
            "role": "user",
            "content": user_message
        }
    ]

    # Pehli call — LLM ko decide karne do kaunsa function chahiye
    response = client.chat.complete(
        model=MODEL,
        messages=messages,
        tools=tools,
        tool_choice="auto"
    )

    response_message = response.choices[0].message
    tool_calls = response_message.tool_calls

    if tool_calls:
        messages.append(response_message)

        # Har tool call ko actually chalao
        for tool_call in tool_calls:
            function_name = tool_call.function.name
            function_args = json.loads(tool_call.function.arguments)

            print(f"[Brain decided: {function_name}({function_args})]")

            function_to_call = available_functions[function_name]
            function_result = function_to_call(**function_args)

            messages.append({
                "role": "tool",
                "name": function_name,
                "content": json.dumps(function_result, default=str),
                "tool_call_id": tool_call.id
            })

        # Doosri call — ab LLM function ka result dekh ke final jawab banayega
        final_response = client.chat.complete(
            model=MODEL,
            messages=messages
        )
        return final_response.choices[0].message.content

    else:
        return response_message.content


# Test karne ke liye
if __name__ == '__main__':
    print("Mail Agent ready! (test mode - text input)\n")

    test_command = "naya mail hai kya important?"
    print(f"User: {test_command}")

    reply = ask_brain(test_command)
    print(f"\nAgent: {reply}")