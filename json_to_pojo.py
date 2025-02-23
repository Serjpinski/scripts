import json
from typing import Any

### Converts a JSON object to a Java POJO initialization that uses Lombok @Builder

# Usage: paste here your json and execute the script
JSON_INPUT = '''
{
  "sentiment": "positive",
  "conceptNames": ["room", "hotel"],
  "concepts": [
    {
      "offset": 28,
      "length": 4
    },
    {
      "offset": 33,
      "length": 7
    }
  ],
  "error": null,
  "success": true
}
'''


INDENT = "    "
ROOT_OBJECT = "RootObject"


def main():
    java_output = process_value(json.loads(JSON_INPUT), ROOT_OBJECT, 0) + ";"
    print(java_output)


def process_value(value: Any, field_name: str, depth: int) -> str:

    if isinstance(value, dict):
        return process_object(value, format_class_name(field_name), depth + 1)

    elif isinstance(value, list):
        if len(value) == 0:
            return "List.of()"
        else:
            list_class_name = format_list_class_name(field_name)

            if isinstance(value[0], dict) or isinstance(value[0], list):
                list_value = ",".join([
                    "\n" + (INDENT * (depth + 1)) + process_value(item, list_class_name, depth + 1) for item in value])
            else:
                list_value = ", ".join([process_value(item, list_class_name, depth) for item in value])

            return f"List.of({list_value})"

    elif isinstance(value, str):
        return f"\"{str(value)}\""

    elif isinstance(value, bool):
        return str(value).lower()

    elif value is None:
        return "null"

    else:
        return str(value)


def process_object(data: dict, class_name: str, depth:int) -> str:

    code = f"{class_name}.builder()"

    for field_name, value in data.items():
        code += (f"\n{INDENT * depth}.{format_field_name(field_name)}"
                 f"({process_value(value, field_name, depth)})")

    code += f"\n{INDENT * depth}.build()"

    return code


def format_field_name(name: str) -> str:

    output = ""
    index = 0

    while index < len(name):

        char = name[index]

        if char == "_":
            index += 1
            if index < len(name):
                output += name[index].upper()
        else:
            output += char

        index += 1

    return output


def format_class_name(name: str) -> str:
    return "".join([char.upper() if index == 0 else char for index, char in enumerate(name)])


def format_list_class_name(name: str) -> str:
    class_name = format_class_name(name)
    return class_name[:-1] if class_name[-1] == "s" else class_name


if __name__ == "__main__":
    main()
