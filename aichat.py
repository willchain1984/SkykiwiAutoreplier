import dashscope
import random
from http import HTTPStatus

def tokenizer():
    response = dashscope.Tokenization.call(
        model="qwen-turbo",
        messages=[{"role": "user", "content": "你好？"}],
    )
    if response.status_code == HTTPStatus.OK:
        print("Result is: %s" % response)
    else:
        print(
            "Failed request_id: %s, status_code: %s, code: %s, message:%s"
            % (
                response.request_id,
                response.status_code,
                response.code,
                response.message,
            )
        )

def call_with_messages(command):
    dashscope.api_key = "sk-fb988c2ad0884a34b16e73168d6d20d1"
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": command},
    ]

    try:
        response = dashscope.Generation.call(
            dashscope.Generation.Models.qwen_turbo,
            messages=messages,
            seed=random.randint(1, 10000),
            result_format="message",  # set the result to be "message" format.
        )
        if response.status_code == HTTPStatus.OK:
            return response
        else:
            print(
                "Request id: %s, Status code: %s, error code: %s, error message: %s"
                % (
                    response.request_id,
                    response.status_code,
                    response.code,
                    response.message,
                )
            )
    except Exception:
        print("Network Error!")
