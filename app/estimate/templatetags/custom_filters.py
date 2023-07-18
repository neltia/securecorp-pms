from django import template
import json

register = template.Library()


@register.filter
def getitem(lst, i):
    return lst[i]


@register.filter
def json_load(string):
    json_data = json.loads(string)
    return json_data


@register.filter
def snake_to_camel(value):
    words = value.split('_')
    return ''.join(word.capitalize() for word in words)


@register.filter
def get_dict_value(dictionary, key):
    return dictionary.get(key)


@register.filter
def list2str(data):
    return ", ".join(data)


@register.filter
def split_last(data, key):
    return data.split(key)[-1]


@register.filter
def estimate_doc_filter(doc_list):
    for doc in doc_list:
        # 프로젝트 유형: 신규/수정
        doc["project_type"] = doc["project_type"].split()[0]

        # 공수산정 요청 승인 여부
        if not doc["is_approved"]:
            doc["is_approved"] = "X"
            doc["approved_date"] = ""
        else:
            doc["is_approved"] = "O"

        if len(doc["project_name"]) > 25:
            doc["project_name"] = doc["project_name"][:20] + "..."
    return doc_list
